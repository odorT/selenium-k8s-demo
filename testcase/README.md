# Test Case

This directory contains actual test cases and dockerfile. Python builtin unittest library is used for testing. There are total of 3 test cases and they are executed concurrently with python's `ThreadPoolExecutor` function from `futures` library. Pytest would have been a better option here since there are some [utility libraries](https://github.com/pytest-dev/pytest-xdist) that automatically handles concurrent test execution. I chose unittesst for simplicity. 


## Test Cases:
**test_homepage_visible**: asserts if page is properly loaded by checking title

**test_careers_page**: checks if elements are present and visible in page. 2 small utility functions are used (_check_element_present, _check_element_visible) which utilizes `WebDriverWait` function with expected_conditions and timeout.

**test_qa_jobs_in_careers_page**: this testcase verifies several things(may seem like a code smell(checking many things in one testcase). But dividing it would probably introduce code duplication or additional complexity, or make testcases depend on each other. Hence, I decided to put all in one). Location button in careers page lazy loads data, therefore it is not available when page is loaded(ajax). When dropdown menu is open, data is not shown either. So I did this: open dropdown menu, check if item is present, close if not and wait for 2 seconds. Later parts are straightforward.


## Test Controller pod image
This container image installs necessary libraries and includes test cases. Note that, Dockerfile does not include CMD or ENTRYPOINT, they are provided from k8s deployment (via commands and args directives).

To build the container image, run:
```shell
VERSION=v0.8 && docker build -t odort/selenium-k8s-demo:$VERSION . && docker push odort/selenium-k8s-demo:$VERSION
```
