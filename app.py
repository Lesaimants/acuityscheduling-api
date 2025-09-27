#!/usr/bin/env python3
import aws_cdk as cdk
from project.stack import ProjectStack

app = cdk.App()

def get_config():
    environment_parameters = app.node.try_get_context(key="sbx")
    return environment_parameters


ProjectStack(app, "AcuityAppointmentsStack", get_config())

app.synth()
