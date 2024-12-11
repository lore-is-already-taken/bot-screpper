FROM ubuntu:20.04

RUN apt update
RUN apt upgrade -y
RUN apt install openssh-server -y
RUN apt install net-tools -y
RUN apt install sshpass -y
RUN apt install iputils-ping -y
RUN apt install neovim -y

# Set up SSH configuration (you may have other configurations)
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Create a new user with the username passed as an argument during build
ARG USERNAME
ARG USER_PASSWORD
RUN useradd -m -s /bin/bash $USERNAME && \
    echo "$USERNAME:$USER_PASSWORD" | chpasswd && \
    usermod -aG sudo $USERNAME


# Set the working directory for the new user
WORKDIR /home/$USERNAME

# Start SSH service on container startup and keep the container alive
ENTRYPOINT service ssh start && tail -f /dev/null

# set root password
RUN echo 'root:toor' | chpasswd && passwd -d root

# Start the SSH daemon (this is the default CMD when starting the container)
CMD ["/usr/sbin/sshd", "-D"]
