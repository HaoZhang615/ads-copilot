param name string
param location string
param containerAppsEnvironmentId string
param containerRegistryLoginServer string
param imageName string
param targetPort int
param managedIdentityId string
param env array = []
param secrets array = []
param isExternal bool = true
param healthProbePath string = '/'

var hasImage = imageName != ''

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: isExternal
        targetPort: targetPort
        transport: 'auto'
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId
        }
      ]
      secrets: secrets
    }
    template: {
      containers: [
        {
          name: name
          image: hasImage ? imageName : 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: env
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: healthProbePath
                port: targetPort
              }
              periodSeconds: 30
              failureThreshold: 3
              initialDelaySeconds: 10
            }
            {
              type: 'Readiness'
              httpGet: {
                path: healthProbePath
                port: targetPort
              }
              periodSeconds: 10
              failureThreshold: 3
              initialDelaySeconds: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
