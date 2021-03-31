![Empire](https://user-images.githubusercontent.com/20302208/70022749-1ad2b080-154a-11ea-9d8c-1b42632fd9f9.jpg)

[1]: https://www.bc-security.org/blog

![GitHub Release](https://img.shields.io/github/v/release/BC-SECURITY/Empire)
![GitHub contributors](https://img.shields.io/github/contributors/BC-SECURITY/Empire)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/BC-SECURITY/Empire)
![GitHub stars](https://img.shields.io/github/stars/BC-SECURITY/Empire)
![GitHub](https://img.shields.io/github/license/BC-Security/Empire)
[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/fold_left.svg?style=flat)](https://twitter.com/BCSecurity1)
[![Discord](https://img.shields.io/discord/716165691383873536)](https://discord.gg/P8PZPyf)

Keep up-to-date on our blog at [https://www.bc-security.org/blog][1]

[Starkiller](https://github.com/BC-SECURITY/Starkiller) | [Empire CLI](https://github.com/BC-SECURITY/Empire-Cli)

# Empire
Empire 3 is a post-exploitation framework that includes a pure-PowerShell Windows agent, and compatibility with Python 3.x Linux/OS X agents. It is the merger of the previous PowerShell Empire and Python EmPyre projects. The framework offers cryptologically-secure communications and flexible architecture.

On the PowerShell side, Empire implements the ability to run PowerShell agents without needing powershell.exe, rapidly deployable post-exploitation modules ranging from key loggers to Mimikatz, and adaptable communications to evade network detection, all wrapped up in a usability-focused framework. PowerShell Empire premiered at [BSidesLV in 2015](https://www.youtube.com/watch?v=Pq9t59w0mUI) and Python EmPyre premiered at HackMiami 2016. BC Security presented updates to further evade Microsoft Antimalware Scan Interface (AMSI) and JA3/S signatures at [DEF CON 27](https://github.com/BC-SECURITY/DEFCON27).

Empire relies heavily on the work from several other projects for its underlying functionality. We have tried to call out a few of those people we've interacted with [heavily here](http://www.powershellempire.com/?page_id=2) and have included author/reference link information in the source of each Empire module as appropriate. If we have failed to properly cite existing or prior work, please let us know at Empire@BC-Security.org.

Empire is currently being developed and maintained by [@Cx01N](https://twitter.com/Cx01N_), [@Hubbl3](https://twitter.com/_Hubbl3), & [@Vinnybod](https://twitter.com/AZHalcyon). While the main Empire project is no longer maintained, this fork is maintained by [@bcsecurity1](https://twitter.com/BCSecurity1). 
Please reach out to us on our [Discord](https://discord.gg/P8PZPyf) if you have any questions or talk about offensive security.

Thank you to the original team of developers: [@harmj0y](https://twitter.com/harmj0y), [@sixdub](https://twitter.com/sixdub), [@enigma0x3](https://twitter.com/enigma0x3), [@rvrsh3ll](https://twitter.com/424f424f), [@killswitch_gui](https://twitter.com/killswitch_gui), & [@xorrior](https://twitter.com/xorrior)

## Sponsors
[<img src="https://user-images.githubusercontent.com/20302208/104083160-41552780-51f1-11eb-8428-3b8cfaf76861.png" width="300"/>](https://www.kali.org/)
[<img src="https://user-images.githubusercontent.com/20302208/113086242-219d2200-9196-11eb-8c91-84f19c646873.png" width="100"/>](https://kovert.no/)

## Release Notes
As of Empire 3.1, we will no longer be actively supporting the Python 2.7 base code. If you wish to continue to leverage Python 2.7 then please use the [3.0.x Releases](https://github.com/BC-SECURITY/Empire/releases), since they were built to ensure backward compatibility.

Please see our [Releases](https://github.com/BC-SECURITY/Empire/releases) or [Changelog](/changelog) page for detailed release notes.

## Install
We recommend the use of [Kali](https://www.kali.org/downloads/), [Poetry](https://python-poetry.org/docs/), or our [Docker images](https://hub.docker.com/r/bcsecurity/empire) to run Empire.
Kali Linux users and [Direct Sponsors](https://github.com/sponsors/BC-SECURITY) will receive 30-day early access to new Empire and Starkiller features.

The following operating systems have been tested for Empire compatibility. We will be unable to provide support for other OSs at this time. Consider using our [Prebuilt Docker containers](#Docker) which can run on any system.
- Kali Linux
- Ubuntu
- Debian

### Kali
You can install the latest version of Empire by running the following:

```sh
sudo apt install powershell-empire
sudo powershell-empire
```

__Note:__ Newer versions of Kali require you to run ```sudo``` before starting Empire.


### Github
Poetry is a dependency and virtual environment management tool. This is highly recommended if using the SocketIO notification feature introduced in 3.5.0. To install Poetry, please follow the installation guide in the documentation or run `sudo pip3 install poetry`.

To install and run:
```sh
git clone --recursive https://github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup/install.sh
sudo poetry install
sudo poetry run python empire
```


### Docker
If you want to run Empire using a pre-built docker container:
```bash
docker pull bcsecurity/empire:{version}
docker run -it -p 1337:1337 -p 5000:5000 bcsecurity/empire:{version}

# with persistent storage
docker pull bcsecurity/empire:{version}
docker create -v /empire --name data bcsecurity/empire:{version}
docker run -it -p 1337:1337 -p 5000:5000 --volumes-from data bcsecurity/empire:{version}

# if you prefer to be dropped into bash instead of directly into empire
docker run -it -p 1337:1337 -p 5000:5000 --volumes-from data bcsecurity/empire:{version} /bin/bash
```

All image versions can be found at: https://hub.docker.com/r/bcsecurity/empire/
* The last commit from master will be deployed to the `latest` tag
* The last commit from the dev branch will be deployed to the `dev` tag
* All github tagged releases will be deployed using their version numbers (v3.0.0, v3.1.0, etc)

## Quickstart
Check out the [Empire wiki](https://github.com/BC-SECURITY/Empire/wiki/Quickstart) for instructions on getting started with Empire.

## Plugins
Plugins are an extension of Empire that allow for custom scripts to be loaded. This allows anyone to easily build or add
community projects to extend Empire functionality. Plugins can be accessed from the Empire CLI or the API as long as the 
plugin follows the [template example](./plugins/example.py). A list of Empire Plugins is located [here](plugins/PLUGINS.md).

## Contribution Rules
Contributions are more than welcome! The more people who contribute to the project the better Empire will be for everyone. Below are a few guidelines for submitting contributions.

* As of Empire 3.1.0, Empire only officially supports Python 3. If you still need Python 2 support, please use the [3.0.x branch](https://github.com/BC-SECURITY/Empire/tree/3.0.x) or releases.
* Submit pull requests to the [dev branch](https://github.com/BC-SECURITY/Empire/tree/dev). After testing, changes will be merged to master.
* Depending on what you're working on, base your module on [./lib/modules/powershell_template.py](lib/modules/powershell_template.py) or [./lib/modules/python_template.py](lib/modules/python_template.py). **Note** that for some modules you may need to massage the output to get it into a nicely displayable text format [with Out-String](https://github.com/PowerShellEmpire/Empire/blob/0cbdb165a29e4a65ad8dddf03f6f0e36c33a7350/lib/modules/situational_awareness/network/powerview/get_user.py#L111).
* Cite previous work in the **'Comments'** module section.
* If your script.ps1 logic is large, may be reused by multiple modules, or is updated often, consider implementing the logic in the appropriate **data/module_source/*** directory and [pulling the script contents into the module on tasking](https://github.com/PowerShellEmpire/Empire/blob/0cbdb165a29e4a65ad8dddf03f6f0e36c33a7350/lib/modules/situational_awareness/network/powerview/get_user.py#L85-L95).
* Use [approved PowerShell verbs](https://technet.microsoft.com/en-us/library/ms714428(v=vs.85).aspx) for any functions.
* PowerShell Version 2 compatibility is **STRONGLY** preferred.
* TEST YOUR MODULE! Be sure to run it from an Empire agent and test Python 3.x functionality before submitting a pull to ensure everything is working correctly.
* For additional guidelines for your PowerShell code itself, check out the [PowerSploit style guide](https://github.com/PowerShellMafia/PowerSploit/blob/master/README.md).

## Official Discord Channel
<p align="center">
<a href="https://discord.gg/P8PZPyf">
<img src="https://discordapp.com/api/guilds/716165691383873536/widget.png?style=banner3"/>
</p>
