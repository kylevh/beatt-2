import groovy.transform.Field
import com.eviware.soapui.support.UISupport

@Field def projects = com.eviware.soapui.SoapUI.getWorkspace().getProjectList()
@Field def projectNames = ["Tax-Pro"]
@Field def ignoreSuites = ["DEV (Old)", "SAT (Old)"]
@Field def devEnvironment = ["DEV", "DEV-PWAS"]
@Field def satEnvironment = ["SAT", "SAT-PWAS"]

def projectFileDir = context.testCase.testSuite.project.path
def projectFolderDir = new File(projectFileDir).getParentFile()
def outputFolder = new File(projectFolderDir, "output")
initializeFolder(outputFolder, true)

def main(outputFolder) {
    // verifyVariables()
    processProjects(outputFolder)
}

def verifyVariables() {
    log.info("Variables verified!")
}

def initializeFolder(File folder, Boolean clear = false) {
    if (folder.exists()) {
        if (clear) {
            folder.eachFile { file ->
                if (file.isDirectory()) clearFolder(file)
                file.delete()
            }
            log.info("FOLDER [${folder.getName()}] already exists, clearing content")
        } else {
            log.info("FOLDER [${folder.getName()}] already exists, leaving as is")
        }
    } else {
        folder.mkdirs()
        log.info("FOLDER [${folder.getName()}] not found, creating new folder!")
    }
}

def escapeForHTML(value) {
    return value?.replaceAll("&", "&amp;")
        ?.replaceAll("<", "&lt;")
        ?.replaceAll(">", "&gt;")
        ?.replaceAll("\"", "&quot;")
        ?.replaceAll("'", "&#39;") ?: ""
}

def getRestCoverage(restTestStep) {
    if (restTestStep.isDisabled()) return 'disabled'
    def result = restTestStep.run(testRunner, context)
    def status = result.getStatus();
    log.info("${restTestStep.name}=====================")
    log.info("Pass/Fail: " + status);
    restTestStep.getAssertionList().each { assertion ->
        log.info("${assertion.getClass().getSimpleName()}: ${assertion.getStatus()}")
    }
    return status.toString() == 'OK' ? 'y' : 'n'
}

def getAssertionResults(restTestStep) {
    def notes = [];
    restTestStep.getAssertionList().each { assertion ->
        def assertionResult = assertion.getStatus().toString();
        if(assertionResult == 'VALID') {
            notes.add("${assertion.getClass().getSimpleName()}: PASSED")
        }
        else if(assertionResult == 'FAILED') {
            notes.add("${assertion.getClass().getSimpleName()}: FAILED")
        }
        else {
            notes.add("${assertion.getClass().getSimpleName()}: UNKNOWN")
        }
    }
    return notes.join("\n");
}

def processProjects(outputFolder) {
    projects.findAll { project -> projectNames.contains(project.name) }.each { project ->
        def outputFilePath = "${outputFolder}/${project.name}-DATAEXPORT.html"
        // log.info("Generating HTML for project: ${project.name}")

        def writer = new File(outputFilePath).withWriter { writer ->
            def id = 1
            writeHtmlHeader(writer, project.name)

            project.getTestSuiteList().each { testSuite ->
                // def testSuite = testSuiteEntry.value
                if (ignoreSuites.contains(testSuite.name)) return

                writeSuiteRow(writer, testSuite.name)

                testSuite.getTestCaseList().each { testCase ->
                    // def testCase = testCaseEntry.value
                    testCase.getTestStepList().each { testStep ->
                        // def testStep = testStepEntry.value

                        if (!(testStep instanceof com.eviware.soapui.impl.wsdl.teststeps.RestTestRequestStep)) {
                            log.info("[ERROR]: Skipping test step - ${testStep.name} due to not being REST ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                            return
                        }

                        def request = testStep.getHttpRequest()
                        def resourcePath = request.path
                        def httpMethod = request.method.toString()
                        def dataMethods = getDataMethods(request)
                                                def devCoverage = ""
                                                def satCoverage = ""

                        // JUST TO LIMIT TO 5 FOR PERFORMANCE
                                                if(id < 5) {
                                devCoverage = devEnvironment.contains(testSuite.name) ? getRestCoverage(testStep) : ""
                                satCoverage = satEnvironment.contains(testSuite.name) ? getRestCoverage(testStep) : ""
                                                }

                        // Get assertion details if failed
                        def assertionNotes = getAssertionResults(testStep);

                        writeHtmlRow(writer, id, devCoverage, satCoverage, resourcePath, testCase.name, httpMethod, testStep.name, dataMethods, assertionNotes)
                        id++
                    }
                }
            }
            writeHtmlFooter(writer)
        }
        log.info("HTML file generated at: ${outputFilePath}")
    }
}

def getDataMethods(request) {
    def dataMethods = []
    if (!request.getRequestContent().isEmpty()) dataMethods.add("Request Body (JSON)")
    if (!request.getParams().isEmpty()) dataMethods.add("Request Params")
    if (!request.getRequestHeaders().isEmpty()) dataMethods.add("Header Params")
    return dataMethods.join(", ")
}

def writeHtmlHeader(writer, projectName) {
    writer.writeLine("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>${projectName} Backend Tracker</title>
            <style>
                body { font-family: Arial, sans-serif; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; }
                th { background-color: #f2f2f2; }
                .suite-row { font-weight: bold; background-color: #FFFF00; text-align: center; }
            </style>
        </head>
        <body>
            <h1>${projectName} Backend Automation Test Coverage</h1>
            <table>
                <tr>
                    <th>ID</th>
                    <th>DEV Coverage</th>
                    <th>SAT Coverage</th>
                    <th>Functional Coverage</th>
                    <th>API</th>
                    <th>Functionality</th>
                    <th>Method</th>
                    <th>Scenario</th>
                    <th>Data Methods</th>
                    <th>Notes</th>
                </tr>
    """)
}

def writeSuiteRow(writer, suiteName) {
    writer.writeLine("<tr><td colspan='10' class='suite-row'>${escapeForHTML(suiteName)} SUITE</td></tr>")
}

def writeHtmlRow(writer, id, devCoverage, satCoverage, resourcePath, functionality, method, scenario, dataMethods, notes = "") {
    writer.writeLine("""
        <tr>
            <td>${id}</td>
            <td>${escapeForHTML(devCoverage)}</td>
            <td>${escapeForHTML(satCoverage)}</td>
            <td></td>
            <td>${escapeForHTML(resourcePath)}</td>
            <td>${escapeForHTML(functionality)}</td>
            <td>${escapeForHTML(method)}</td>
            <td>${escapeForHTML(scenario)}</td>
            <td>${escapeForHTML(dataMethods)}</td>
            <td>${notes}</td>
        </tr>
    """)
}

def writeHtmlFooter(writer) {
    writer.writeLine("""
            </table>
        </body>
        </html>
    """)
}

main(outputFolder)

UISupport.showInfoMessage("Script ran succesffully with no errors i think", "Task completed");