param name string
param location string
param logAnalyticsCustomerId string
@secure()
param logAnalyticsSharedKey string

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsSharedKey
      }
    }
  }
}

output id string = containerAppsEnv.id
output defaultDomain string = containerAppsEnv.properties.defaultDomain
