# Start from Python on Debian
# https://devguide.python.org/versions/
# https://wiki.debian.org/LTS
FROM python:3.12-bookworm


# Install Python tooling
RUN pip install pipx==1.7.1
RUN pipx install poetry==2.0.1
RUN pipx install invoke==2.2.0
ENV PATH="/root/.local/bin:${PATH}"

# Install docker-in-docker
# https://github.com/devcontainers/features/tree/main/src/docker-in-docker
RUN export DOCKER_VERSION=27.5.1 && \
    wget --output-document - https://raw.githubusercontent.com/devcontainers/features/5c67da03b794f207e45aa34e04fddcb2fa3e5aaa/src/docker-in-docker/install.sh | bash


# Install AWS CLI
RUN apt-get update && \
    apt-get install --assume-yes awscli=2.9.19-1


# Install AWS CDK CLI
# - NodeJS
#   https://github.com/nodejs/release#release-schedule
#   https://github.com/nodesource/distributions
RUN wget --output-document - https://deb.nodesource.com/setup_22.x | bash && \
    apt-get install --assume-yes nodejs
# - aws-cdk
#   The CLI version should be synchronized with the library version.
#   https://www.npmjs.com/package/aws-cdk?activeTab=versions
RUN npm install -g aws-cdk@2.178.2


# Install AWS SAM CLI
# https://github.com/aws/aws-sam-cli/releases
RUN arch=$(case $(uname -m) in aarch64) echo arm64;; *) echo x86_64;; esac) && \
    file="aws-sam-cli-linux-$arch.zip" && \
    wdir=$(mktemp -d) && \
    wget --output-document $file "https://github.com/aws/aws-sam-cli/releases/download/v1.133.0/$file" && \
    unzip -q -o $file -d $wdir && \
    $wdir/install && \
    rm -rf $wdir && \
    rm $file


# Initialize
# - Start Docker daemon (from docker-in-docker)
ENTRYPOINT ["/bin/bash", "/usr/local/share/docker-init.sh"]

CMD ["sleep", "infinity"]
