targetScope = 'resourceGroup'

param environmentName string
param location string = resourceGroup().location
param backendImageName string = ''
param frontendImageName string = ''
@secure()
param copilotGithubToken string
param avatarEnabled bool = true
param avatarCharacter string = 'lisa'
param avatarStyle string = 'casual-sitting'
param avatarVoice string = 'en-US-AvaMultilingualNeural'


var abbrevs = {
  logAnalytics: 'log'
  containerRegistry: 'cr'
  containerAppsEnv: 'cae'
  managedIdentity: 'id'
  cognitiveServices: 'cog'
  keyVault: 'kv'
  logicApp: 'la'
  backendApp: 'ca'
  frontendApp: 'ca'
}

var registryName = replace('${abbrevs.containerRegistry}${environmentName}', '-', '')

module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'log-analytics'
  params: {
    name: '${abbrevs.logAnalytics}-${environmentName}'
    location: location
  }
}

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'container-registry'
  params: {
    name: registryName
    location: location
  }
}

module containerAppsEnv 'modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  params: {
    name: '${abbrevs.containerAppsEnv}-${environmentName}'
    location: location
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsSharedKey: logAnalytics.outputs.sharedKey
  }
}

module managedIdentity 'modules/managed-identity.bicep' = {
  name: 'managed-identity'
  params: {
    name: '${abbrevs.managedIdentity}-${environmentName}'
    location: location
  }
}

module cognitiveServices 'modules/cognitive-services.bicep' = {
  name: 'cognitive-services'
  params: {
    name: '${abbrevs.cognitiveServices}-${environmentName}'
    location: location
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'key-vault'
  params: {
    name: '${abbrevs.keyVault}-${environmentName}'
    location: location
    principalId: managedIdentity.outputs.principalId
    copilotGithubToken: copilotGithubToken
  }
}

module logicApp 'modules/logic-app.bicep' = {
  name: 'logic-app'
  params: {
    name: '${abbrevs.logicApp}-${environmentName}'
    location: location
  }
}

module roleAssignments 'modules/role-assignments.bicep' = {
  name: 'role-assignments'
  params: {
    principalId: managedIdentity.outputs.principalId
    cognitiveServicesAccountName: cognitiveServices.outputs.name
    containerRegistryName: containerRegistry.outputs.name
  }
}

module backendApp 'modules/container-app.bicep' = {
  name: 'backend-app'
  params: {
    name: '${abbrevs.backendApp}-${environmentName}-backend'
    location: location
    containerAppsEnvironmentId: containerAppsEnv.outputs.id
    containerRegistryLoginServer: containerRegistry.outputs.loginServer
    imageName: backendImageName
    targetPort: 8000
    managedIdentityId: managedIdentity.outputs.id
    healthProbePath: '/health'
    serviceName: 'backend'
    env: [
      {
        name: 'AZURE_VOICELIVE_ENDPOINT'
        value: cognitiveServices.outputs.endpoint
      }
      {
        name: 'AZURE_VOICELIVE_API_VERSION'
        value: '2025-10-01'
      }
      {
        name: 'AZURE_VOICELIVE_MODEL'
        value: 'gpt-realtime'
      }
      {
        name: 'AZURE_SPEECH_REGION'
        value: location
      }
      {
        name: 'AZURE_SPEECH_SERVICE_ID'
        value: cognitiveServices.outputs.id
      }
      {
        name: 'AZURE_CLIENT_ID'
        value: managedIdentity.outputs.clientId
      }
      {
        name: 'BACKEND_HOST'
        value: '0.0.0.0'
      }
      {
        name: 'BACKEND_PORT'
        value: '8000'
      }
      {
        name: 'CORS_ORIGINS'
        value: 'https://${abbrevs.frontendApp}-${environmentName}-frontend.${containerAppsEnv.outputs.defaultDomain}'
      }
      {
        name: 'COPILOT_GITHUB_TOKEN'
        secretRef: 'copilot-github-token'
      }
      {
        name: 'AVATAR_ENABLED'
        value: string(avatarEnabled)
      }
      {
        name: 'AVATAR_CHARACTER'
        value: avatarCharacter
      }
      {
        name: 'AVATAR_STYLE'
        value: avatarStyle
      }
      {
        name: 'AVATAR_VOICE'
        value: avatarVoice
      }
      {
        name: 'LOGIC_APP_TRIGGER_URL'
        value: logicApp.outputs.triggerUrl
      }
    ]
    secrets: [
      {
        name: 'copilot-github-token'
        keyVaultUrl: '${keyVault.outputs.vaultUri}secrets/copilot-github-token'
        identity: managedIdentity.outputs.id
      }
    ]
  }
  dependsOn: [
    roleAssignments
  ]
}

module frontendApp 'modules/container-app.bicep' = {
  name: 'frontend-app'
  params: {
    name: '${abbrevs.frontendApp}-${environmentName}-frontend'
    location: location
    containerAppsEnvironmentId: containerAppsEnv.outputs.id
    containerRegistryLoginServer: containerRegistry.outputs.loginServer
    imageName: frontendImageName
    targetPort: 3000
    managedIdentityId: managedIdentity.outputs.id
    healthProbePath: '/'
    serviceName: 'frontend'
    env: [
      {
        name: 'BACKEND_WS_URL'
        value: 'wss://${backendApp.outputs.fqdn}/ws'
      }
      {
        name: 'BACKEND_API_URL'
        value: 'https://${backendApp.outputs.fqdn}'
      }
    ]
  }
  dependsOn: [
    roleAssignments
  ]
}

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output BACKEND_URL string = backendApp.outputs.uri
output FRONTEND_URL string = frontendApp.outputs.uri
output AZURE_VOICELIVE_ENDPOINT string = cognitiveServices.outputs.endpoint
output LOGIC_APP_TRIGGER_URL string = logicApp.outputs.triggerUrl
