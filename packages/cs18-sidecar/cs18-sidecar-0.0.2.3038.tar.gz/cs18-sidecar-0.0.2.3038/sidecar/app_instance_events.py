class AppInstanceEvents:
    DownloadingArtifacts = "Downloading artifacts"
    WaitingForDependencies = "Waiting for dependencies"
    RunningInitialization = "Running initialization"
    RunningStartCommand = "Running start command"
    RunningHealthCheck = "Running healthcheck"
    DeploymentCompleted = "Deployment ended successfully"
    DeploymentFailed = "Deployment failed"

    ALL = [
        DownloadingArtifacts,
        WaitingForDependencies,
        RunningInitialization,
        RunningHealthCheck,
        RunningStartCommand,
        DeploymentCompleted,
        DeploymentFailed
    ]
