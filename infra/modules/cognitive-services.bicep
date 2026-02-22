param name string
param location string
// customSubDomainName is required for the named endpoint format
// (e.g., cog-xxx.services.ai.azure.com) which Voice Live requires.
var customSubDomainName = name
resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    customSubDomainName: customSubDomainName
  }
}

// Voice Live requires the resource-name-based endpoint, NOT the regional one.
// Format: https://<name>.cognitiveservices.azure.com/
output endpoint string = cognitiveServices.properties.endpoint
output id string = cognitiveServices.id
output name string = cognitiveServices.name
