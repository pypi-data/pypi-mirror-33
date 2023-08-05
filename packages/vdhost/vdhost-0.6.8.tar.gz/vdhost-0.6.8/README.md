# vectordash-host
A command line tool for hosting your machine as [Vectordash](http://vectordash.com) GPU instances.

For a more detailed overview on how to get started, how the commands work, or general questions, please go to our [docs](https://docs.vectordash.com)!

#### Usage Examples

1) `vdhost install` - Install dependencies on the host machine to configure it for hosting

2) `vdhost is-running` - Check if the client daemon process is running on this machine

3) `vdhost login` - Allows the user to authenticate themselves and their machine

4) `vdhost set-commands` - Allows user to set up miner on their machine

5) `vdhost start-hosting` - Runs the client daemon that brings the machine online and hosts it on Vectordash

6) `vdhost stop-hosting` - Stops the client daemon and removes the machine from being hosted on Vectordash

7) `vdhost start-miner GPU_ID` - Starts the miner of your choice for the provided GPU (id)

8) `vdhost stop-miner GPU_ID` - Stops the miner for the provided GPU (id)
