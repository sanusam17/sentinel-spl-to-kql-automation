kql = """
AzureActivity
| where OperationNameValue =~ "MICROSOFT.INSIGHTS/DIAGNOSTICSETTINGS/DELETE"
| summarize count() by Caller
"""

with open("kql-rules/rule.kql", "w") as f:
    f.write(kql)

print("KQL file generated successfully")