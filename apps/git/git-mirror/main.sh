#!/bin/bash
set +x

# This script takes a CSV file as input and mirrors repos and pushes them to new GitHub (private) repos.

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <path_to_csv>"
  exit 1
fi

CSV_FILE="$1"
MIRROR_REPO_PREFIX=${MIRROR_REPO_PREFIX:-"mirror"}
TARGET_REPO_IS_PRIVATE=${TARGET_REPO_IS_PRIVATE:-"true"}
GITHUB_TOKEN="${GITHUB_TOKEN}"
GITHUB_CREATE_REPO_API_URL="https://api.github.com/user/repos"
BFG_TOOL="java -jar $(pwd)/tools/bfg.jar"
TARGET_REPO_USER=${TARGET_REPO_USER:-"mirror"}

while IFS=, read -r source_git_url; do
  # Extract repo name from the GitLab URL
  source_repo_name=$(echo "$source_git_url" | awk -F'/' '{print $NF}' | awk -F'.git' '{print $1}')
  echo "SOURCE REPO NAME: $source_repo_name"

  target_repo_name="${MIRROR_REPO_PREFIX}-${source_repo_name}"
  echo "TARGET REPO NAME: $target_repo_name"

  cd repos || exit

  # Clone the GitLab repo
  if [ ! -d "$target_repo_name" ]; then
    echo "CLONING SOURCE REPO $source_repo_name LOCALLY TO $target_repo_name"
    git clone --git-mirror "$source_git_url" "$target_repo_name"
  fi

  # Enter the repository directory
  cd "$target_repo_name" || exit

  # Create a new repository on GitHub
  echo "CREATING TARGET REPO AT GITHUB $target_repo_name"
  repo_creation_response=$(curl -s -X POST $GITHUB_CREATE_REPO_API_URL \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{ \"name\": \"$target_repo_name\", \"private\": ${TARGET_REPO_IS_PRIVATE}")

  # Extract the new repo's URL from the response
  target_repo_url=$(echo "$repo_creation_response" | jq -r .clone_url)

  # If there was an error creating the repo, display a message and exit the loop
  if [ "$target_repo_url" == "null" ]; then
    repo_exists=$(echo "$repo_creation_response" | jq -r '.errors[]? | select(.message == "name already exists on this account") | .message')

    if [[ $repo_exists == "name already exists on this account" ]]; then
      target_repo_url="https://github.com/${TARGET_REPO_USER}/${target_repo_name}.git"
      echo "REPOSITORY $target_repo_name ALREADY EXISTS!"
    else
      echo "ERROR CREATING REPOSITORY FOR $target_repo_name. SKIPPING..."
      echo "$repo_creation_response"
      cd ../..
      continue
    fi
  fi

  # Push the repository to GitHub
  target_repo_url_with_auth_token=${target_repo_url/https:\/\//https://${GITHUB_TOKEN}@}

  # github doesn't allow files that 100MB
  echo "CLEANING FILES LARGER THAN 100MB using BFG TOOL"
  $BFG_TOOL -b 100M

  echo "MIRRORING SOURCE REPO $source_repo_name TO $target_repo_name"
  git push --git-mirror "${target_repo_url_with_auth_token}"

  # Go back to the previous directory and clean up
  cd ../..
done <"$CSV_FILE"

echo "PROCESS COMPLETED!"
