#!/usr/bin/env python3

import os
import aws_cdk as cdk
from lib.selenium_stack import SeleniumStack


app = cdk.App()
SeleniumStack(app, "SeleniumStack",env=cdk.Environment(
                account="",
                region="eu-west-2"
            ))

app.synth()
