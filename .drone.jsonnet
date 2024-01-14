local name = "files";
local browser = "firefox";
local selenium = "4.0.0-beta-3-prerelease-20210402";
local deployer = "https://github.com/syncloud/store/releases/download/4/syncloud-release";

local build(arch, test_ui, dind) = [ {
    kind: "pipeline",
    type: "docker",
    name: arch,
    platform: {
        os: "linux",
        arch: arch
    },
    steps: [
     {
            name: "version",
            image: "debian:buster-slim",
            commands: [
                "echo $DRONE_BUILD_NUMBER > version"
            ]
        },
         {
               name: "build python",
            image: "docker:" + dind,
            commands: [
                "./python/build.sh"
            ],
            volumes: [
                {
                    name: "dockersock",
                    path: "/var/run"
                }
            ]
           },
        {
            name: "download",
            image: "debian:buster-slim",
            commands: [
                "./download.sh " + name
            ]
        },
        {
            name: "build",
            image: "debian:buster-slim",
            commands: [
               "VERSION=$(cat version)",
                "./build.sh " + name + " $VERSION "
            ]
        },
        {
            name: "package",
            image: "debian:buster-slim",
            commands: [
                "VERSION=$(cat version)",
                "./package.sh " + name + " $VERSION"
            ]
        },
        {
            name: "test-integration-buster",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client netcat",
              "APP_ARCHIVE_PATH=$(realpath $(cat package.name))",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s verify.py --distro=buster --domain=buster.com --app-archive-path=$APP_ARCHIVE_PATH --device-host=" + name + ".buster.com --app=" + name
            ]
        }] + ( if test_ui then [
        {
            name: "test-ui-desktop-buster",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client netcat",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s test-ui.py --distro=buster --ui-mode=desktop --domain=buster.com --device-host=" + name + ".buster.com --app=" + name + " --browser=" + browser,
            ],
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        },
        {
            name: "test-ui-mobile-buster",
            image: "python:3.8-slim-buster",
            commands: [
              "apt-get update && apt-get install -y sshpass openssh-client netcat",
              "cd integration",
              "pip install -r requirements.txt",
              "py.test -x -s test-ui.py --distro=buster --ui-mode=mobile --domain=buster.com --device-host=" + name + ".buster.com --app=" + name + " --browser=" + browser,
            ],
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        } ] else [] ) +[
       {
               name: "upload",
               image: "debian:buster-slim",
               environment: {
                   AWS_ACCESS_KEY_ID: {
                       from_secret: "AWS_ACCESS_KEY_ID"
                   },
                   AWS_SECRET_ACCESS_KEY: {
                       from_secret: "AWS_SECRET_ACCESS_KEY"
                   },
                   SYNCLOUD_TOKEN: {
                       from_secret: "SYNCLOUD_TOKEN"
                   }
               },
               commands: [
                 "PACKAGE=$(cat package.name)",
                 "apt update && apt install -y wget",
                 "wget " + deployer + "-" + arch + " -O release --progress=dot:giga",
                 "chmod +x release",
                 "./release publish -f $PACKAGE -b $DRONE_BRANCH"
                ],
               when: {
                   branch: ["stable", "master"],
                   event: ["push"]
               }
        },
        {
                  name: "promote",
                  image: "debian:buster-slim",
                  environment: {
                      AWS_ACCESS_KEY_ID: {
                          from_secret: "AWS_ACCESS_KEY_ID"
                      },
                      AWS_SECRET_ACCESS_KEY: {
                          from_secret: "AWS_SECRET_ACCESS_KEY"
                      },
                       SYNCLOUD_TOKEN: {
                           from_secret: "SYNCLOUD_TOKEN"
                       }
                  },
                  commands: [
                    "apt update && apt install -y wget",
                    "wget " + deployer + "-" + arch + " -O release --progress=dot:giga",
                    "chmod +x release",
                    "./release promote -n " + name + " -a $(dpkg --print-architecture)"
                  ],
                  when: {
                      branch: ["stable"],
                      event: ["push"]
                  }
            },
        {
            name: "artifact",
            image: "appleboy/drone-scp:1.6.4",
            settings: {
                host: {
                    from_secret: "artifact_host"
                },
                username: "artifact",
                key: {
                    from_secret: "artifact_key"
                },
                timeout: "2m",
                command_timeout: "2m",
                target: "/home/artifact/repo/" + name + "/${DRONE_BUILD_NUMBER}-" + arch,
                source: "artifact/*",
		             strip_components: 1
            },
            when: {
              status: [ "failure", "success" ]
            }
        }
    ],
    trigger: {
      event: [
        "push",
        "pull_request"
      ]
    },
    services: [
 {
            name: "docker",
            image: "docker:" + dind,
            privileged: true,
            volumes: [
                {
                    name: "dockersock",
                    path: "/var/run"
                }
            ]
        },
        {
            name: name + ".buster.com",
            image: "syncloud/platform-buster-" + arch + ":21.10",
            privileged: true,
            volumes: [
                {
                    name: "dbus",
                    path: "/var/run/dbus"
                },
                {
                    name: "dev",
                    path: "/dev"
                }
            ]
        }
    ] + ( if test_ui then [{
            name: "selenium",
            image: "selenium/standalone-" + browser + ":" + selenium,
            volumes: [{
                name: "shm",
                path: "/dev/shm"
            }]
        }
    ] else [] ),
    volumes: [
        {
            name: "dbus",
            host: {
                path: "/var/run/dbus"
            }
        },
        {
            name: "dev",
            host: {
                path: "/dev"
            }
        },
        {
            name: "shm",
            temp: {}
        },
        {
            name: "dockersock",
            temp: {}
        }
    ]
}];

build("amd64", true, "20.10.21-dind") +
build("arm64", false, "19.03.8-dind") +
build("arm", false, "19.03.8-dind")
