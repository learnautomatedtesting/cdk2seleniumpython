import aws_cdk as core
import aws_cdk.assertions as assertions

from lib.lib_stack import LibStack

# example tests. To run these tests, uncomment this file along with the example
# resource in lib/lib_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LibStack(app, "lib")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
