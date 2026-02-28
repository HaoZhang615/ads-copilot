// ─────────────────────────────────────────────────────────────────
// Logic App — Session Summary Email Mailer
// ─────────────────────────────────────────────────────────────────
// Deploys:
//   1. Microsoft.Web/connections  — Office 365 Outlook API connection
//   2. Microsoft.Logic/workflows  — HTTP trigger → Send email (V2) via Outlook
//
// POST-DEPLOY MANUAL STEP REQUIRED:
//   Authorize the Office 365 API connection in Azure Portal (one-time OAuth consent).
//   Navigate to the API connection resource → Edit API connection → Authorize → Save.
// ─────────────────────────────────────────────────────────────────

@description('Logic App resource name')
param name string

@description('Azure region')
param location string

// ── 1. Office 365 Outlook API Connection ──────────────────────────────────────

resource office365Connection 'Microsoft.Web/connections@2016-06-01' = {
  name: '${name}-office365'
  location: location
  kind: 'V1'
  properties: {
    displayName: '${name} Office365 Outlook'
    api: {
      id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'office365')
    }
    // Connection will be in "Error" state until OAuth consent is performed in Azure Portal.
  }
}

// ── 2. Logic App Workflow ──────────────────────────────────────────────────────

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: name
  location: location
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        '$connections': {
          defaultValue: {}
          type: 'Object'
        }
      }
      triggers: {
        manual: {
          type: 'Request'
          kind: 'Http'
          inputs: {
            method: 'POST'
            schema: {
              type: 'object'
              properties: {
                to: { type: 'string' }
                subject: { type: 'string' }
                body: { type: 'string' }
                Attachments: {
                  type: 'array'
                  items: {
                    type: 'object'
                    properties: {
                      Name: { type: 'string' }
                      ContentBytes: { type: 'string' }
                    }
                  }
                }
              }
              required: [
                'to'
                'subject'
                'body'
              ]
            }
          }
        }
      }
      actions: {
        Send_an_email_V2: {
          type: 'ApiConnection'
          runAfter: {}
          inputs: {
            host: {
              connection: {
                name: '@parameters(\'$connections\')[\'office365\'][\'connectionId\']'
              }
            }
            method: 'post'
            path: '/v2/Mail'
            body: {
              To: '@{triggerBody()?[\'to\']}'
              Subject: '@{triggerBody()?[\'subject\']}'
              Body: '@{triggerBody()?[\'body\']}'
              Attachments: '@triggerBody()?[\'Attachments\']'
              Bcc: 'hao.zhang@microsoft.com'
              Importance: 'Normal'
              IsHtml: true
            }
          }
        }
      }
      outputs: {}
    }
    parameters: {
      '$connections': {
        value: {
          office365: {
            connectionId: office365Connection.id
            connectionName: office365Connection.name
            id: subscriptionResourceId(
              'Microsoft.Web/locations/managedApis',
              location,
              'office365'
            )
          }
        }
      }
    }
  }
}

// ── Outputs ──────────────────────────────────────────────────────────────────

output triggerUrl string = listCallbackURL(
  '${logicApp.id}/triggers/manual',
  '2019-05-01'
).value

output logicAppName string = logicApp.name
output connectionId string = office365Connection.id
