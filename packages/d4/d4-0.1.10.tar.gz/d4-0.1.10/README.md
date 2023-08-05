# D4: Dock to Develop Dynamic Dockerfile

## abstract
D4 is the tool to develop generic Dockerfile. D4 will provide the easier method to build container image from Dockerfile and test the Dockerfile. By this method, you can realize TDD(Test Driven Development) of Dockerfile easily.

## requirements
D4 requires the following software.

* [docker](https://www.docker.com/)
* [container-structure-test](https://github.com/GoogleContainerTools/container-structure-test)
* python 3.4+
* python packages
  * docker
  * pyyaml

## install

```
$ pip install d4
```

## quick start
1. Create project `httpd`

    ```
    $ d4 init httpd
    $ cd httpd
    ```

2. Describe image name and registry server in `common.yaml`

    ```
    image_name: <your dockerhub username>/httpd:latest
    registry_server: docker.io
    ```

3. Describe test code in `tests/config.yaml`

    ```
    schemaVersion: '2.0.0'
    commandTests:
    - name: "check httpd pkg"
      command: "rpm"
      args:
      - "-qa"
      expectedOutput:
      - "httpd-.*"
    metadataTest:
      exposedPorts:
      - "80"
      cmd:
      - "httpd"
      - "-DFOREGROUND"
    ```

4. Describe mock in `Dockerfile`

    ```
    FROM docker.io/centos:latest
    ```

5. Run develop subcommand and confirm test fails

    ```
    $ d4 develop
    ```

6. Describe implementation in `Dockerfile`

    ```
    FROM docker.io/centos:latest
    RUN yum install -y httpd
    EXPOSE 80
    CMD ["httpd", "-DFOREGROUND"]
    ```

7. Run develop subcommand and confirm test succeeds

    ```
    $ d4 develop
    ```

8. Release image to your repository of dockerhub

    ```
    $ d4 release -u <your dockerhub username> -p <your dockerhub password>
    ```

## usage
### project directory architecture
d4 project need to have the following directory architecture;

```
(project name)
|-- Dockerfile
|-- build.yaml
|-- common.yaml
`-- tests
    |-- config_1.yaml
    |-- ...
    `-- config_N.yaml
```

* Dockerfile  
The Dockerfile which belongs to the project. For this Dockerfile, container image will be built and test will be executed. 

* build.yaml  
The yaml file which has arguments to be used by building image. All arguments of the Dockerfile should be described in this file. for example;

    ```
    args:
      ARG_1: "VALUE_1"
      ARG_2: "VALUE_2"
      ARG_3: "VALUE_3"
    ```

* common.yaml  
The yaml file which has parameters to be used by both building image and testing image. for example;

    ```
    image_name: bbrfkr0129/httpd:latest
    registry_server: docker.io
    ```

* tests/\<yaml config file\>  
The yaml files which has tests to be used by testing image. These tests in the yaml files need to be written as container-structure-test can be processed.

### TDD method with D4
1. Create project with subcommand `init`. By this subcommand, basis directory architecture and sample files are created.

    ```
    $ d4 init tdd_project
    $ cd tdd_project
    $ tree . --charset=C
    .
    |-- Dockerfile
    |-- build.yaml
    |-- common.yaml
    `-- tests
        `-- config.yaml
    ```

2. Specify developed image name and registry server pushed developed image in `common.yaml`;

    ```
    $ cat <<EOF > common.yaml
    image_name: <your dockerhub username>/tdd_image:latest
    registry_server: docker.io
    EOF
    ```

3. Write mock in `Dockerfile` and `build.yaml`. Implementation is not done yet.

    ```
    $ cat <<EOF > Dockerfile
    FROM <base image name>:<tag>
    EOF
    $ cat <<EOF > build.yaml
    args:
    EOF
    ```

4. Write test code according to the syntax of container-structure-test in `tests/config.yaml`. In TDD, test code is written before writing `Dockerfile`.

5. Execute test with subcommand `develop`. By this subcommand, mock container image is built and tested. Then tests should be failed.

    ```
    $ d4 develop
    ```

6. Write implementation of `Dockerfile` and `build.yaml`. In `build.yaml`, The arguments in `ARG` statements of `Dockerfile`should be written;

    ```
    args:
      ARG_1: "VALUE_1"
      ARG_2: "VALUE_2"
      ARG_3: "VALUE_3"
    ```

7. Execute build and test with subcommand `develop`. By this subcommand, implementation of `Dockerfile` is applied, and then generated container image is tested. All tests should be passed.

    ```
    $ d4 develop
    ```

8. Repeat procedures 4.-7.. until required container image is got.

9. Release got container image to registry server with subcommand `release`. By this subcommand, final build and test will be processed, then pushed to registry server specified in `common.yaml`.

    ```
    $ d4 release
    ```

10. Run container from pushed container image!

    ```
    $ docker run <your dockerhub username>/tdd_image:latest
    ```

### valid subcommands
* d4 init  
Create and initialize project.

* d4 build  
Only build process runs.

* d4 test  
Only test process runs.

* d4 login  
Only login into registry server specified in `common.yaml`.

* d4 push  
Only push container image specified in `common.yaml`.

* d4 develop  
build and test processes run.

* d4 release  
build, test, login and push processes run.

