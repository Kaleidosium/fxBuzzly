from flask import Flask, render_template
from configparser import ConfigParser
import requests

app = Flask(__name__)

config = ConfigParser()
config.read("fxbuzzly.ini")


def get_submission_data(fxbuzzly_username, fxbuzzly_title):
    data = {
        "operationName": "getSubmission",
        "query": "mutation getSubmission($username: String!, $slug: String!) {\n  fetchSubmissionByUsernameAndSlug(input: {username: $username, slug: $slug}) {\n    submission {\n      ...fullSubmission\n    }\n  }\n}\n\nfragment fullSubmission on Submission {\n  id\n  title\n  description\n  tags\n  path\n  thumbnailPath\n  type\n  size\n  created\n  deleted\n  visits\n  width\n  height\n  slug\n  comments\n  ratings\n  favorites\n  textContent\n  contentRating\n  hiddenByStaff\n  bucket: bucketByBucket {\n    name\n  }\n  category: categoryByCategory {\n    ...category\n  }\n  artSubjectCategories: submissionCategoriesBySubmissionId {\n    nodes {\n      category: categoryByCategoryId {\n        ...category\n      }\n    }\n  }\n  account: accountByAccount {\n    id\n    displayName\n    username\n    profilePicturePath\n    hideFromGuests\n    bucket: bucketByBucket {\n      name\n    }\n    user: userByUser {\n      id\n      isAdmin\n      isStaff\n      hideCountry\n      premiumUntil\n      bannedSince\n      bannedUntil\n    }\n  }\n  featuredOn\n  featuredBy: accountByFeaturedBy {\n    ...accountWithUser\n  }\n}\n\nfragment category on Category {\n  id\n  name\n  ordinal\n  parent\n  slug\n  isArtSubject\n  isNsfw\n}\n\nfragment accountWithUser on Account {\n  id\n  displayName\n  username\n  created\n  preference\n  followers\n  profilePicturePath\n  profileHeaderPath\n  commentsSignature\n  bucket: bucketByBucket {\n    name\n  }\n  user: userByUser {\n    id\n    country\n    bannedSince\n    bannedUntil\n    premiumUntil\n    isAdmin\n    isStaff\n    hideCountry\n  }\n  isBot\n  lastOnline\n  hideLastOnline\n  hideFromGuests\n  hideFollowersCount\n  hideFromInvisibleUsers\n}\n",
        "variables": {"username": fxbuzzly_username, "slug": fxbuzzly_title},
    }
    return data


@app.route("/<path:subpath>")
def fxbuzzly_art(subpath):
    split_subpath = subpath.split("/")

    fxbuzzly_username = split_subpath[0].replace("~", "")
    fxbuzzly_title = split_subpath[2]

    response = requests.post(
        "https://graphql.buzzly.art/graphql",
        json=get_submission_data(fxbuzzly_username, fxbuzzly_title),
    )
    origin = "https://buzzly.art/" + subpath

    return render_template(
        "index.html",
        user=response.json()["data"]["fetchSubmissionByUsernameAndSlug"]["submission"][
            "account"
        ]["displayName"]
        + " ("
        + response.json()["data"]["fetchSubmissionByUsernameAndSlug"]["submission"][
            "account"
        ]["username"]
        + ")",
        img="https://submissions.buzzly.art"
        + response.json()["data"]["fetchSubmissionByUsernameAndSlug"]["submission"][
            "path"
        ],
        url=origin,
        desc=response.json()["data"]["fetchSubmissionByUsernameAndSlug"]["submission"][
            "description"
        ],
        site_name=config.get("config", "site_name"),
        colour="#" + config.get("config", "colour"),
    )


if __name__ == "__main__":
    app.run(debug=config.getboolean("config", "debug"))
    app.run(host=config.get("config", "host"), port=config.getint("config", "port"))
