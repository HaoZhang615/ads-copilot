param name string
param location string

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
  }
}

output endpoint string = cognitiveServices.properties.endpoint
output id string = cognitiveServices.id
output name string = cognitiveServices.name
