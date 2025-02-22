#!/bin/zsh

brew install asdf

# Install Plugins
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin add pnpm
asdf plugin add python https://github.com/asdf-vm/asdf-python.git
# asdf plugin add poetry https://github.com/asdf-community/asdf-poetry.git
asdf plugin add pipenv https://github.com/and-semakin/asdf-pipenv.git 

asdf install
asdf reshim

cd llama_local
pipenv install
