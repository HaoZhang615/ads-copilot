param principalId string
param cognitiveServicesAccountName string
param containerRegistryName string

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}
resource cognitiveServicesAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: cognitiveServicesAccountName
}

// Cognitive Services User — required for general API access
resource cognitiveServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(cognitiveServicesAccount.id, principalId, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  scope: cognitiveServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// Azure AI User — required by Voice Live for ai.azure.com scope auth
resource azureAIUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(cognitiveServicesAccount.id, principalId, '53ca6127-db72-4b80-b1b0-d745d6d5456d')
  scope: cognitiveServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// Cognitive Services Speech User — required for Speech TTS Avatar relay token endpoint
resource cognitiveServicesSpeechUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(cognitiveServicesAccount.id, principalId, 'f2dc8367-1007-4938-bd23-fe263f013447')
  scope: cognitiveServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f2dc8367-1007-4938-bd23-fe263f013447')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, principalId, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
