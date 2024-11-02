class Portal {
    String portalName
    List<Project> projects
}

class Project {
    String projectName
    List<TestSuite> testSuites
}

class TestSuite {
    String testSuiteName
    List<TestCase> testCases
}

class TestCase {
    String testCaseName
    String executionTime
    String startTime
    String endTime
    String status
    List<TestStep> testSteps
}

class TestStep {
    String testStepName
    String method
    String url
    Map<String, Object> pathParams
    Map<String, Object> queryParams
    Map<String, String> headers
    Map<String, Object> requestBody
    List<Assertion> assertions
    String status
    String executionTime
    String startTime
    String endTime
}

class Assertion {
    String type
    int expected
    int actual
    String status
    String errorMessage
}