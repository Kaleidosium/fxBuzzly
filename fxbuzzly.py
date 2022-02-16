from flask import Flask, Response, render_template
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
    if subpath.startswith("~"):
        split_subpath = subpath.split("/")

        fxbuzzly_username = split_subpath[0].replace("~", "")
        fxbuzzly_title = split_subpath[2]

        response = requests.post(
            "https://graphql.buzzly.art/graphql",
            json=get_submission_data(fxbuzzly_username, fxbuzzly_title),
        )
        origin = "https://buzzly.art/" + subpath

        submission_response_json = response.json()["data"][
            "fetchSubmissionByUsernameAndSlug"
        ]["submission"]

        if submission_response_json["category"]["isNsfw"]:
            return render_template(
                "index.html",
                user=submission_response_json["account"]["displayName"]
                + " ("
                + submission_response_json["account"]["username"]
                + ")",
                url=origin,
                desc="Image embeds are not available for NSFW submissions.",
                site_name=config.get("site_config", "site_name"),
                colour="#" + config.get("site_config", "colour"),
            )
        if submission_response_json["account"]["hideFromGuests"]:
            return render_template(
                "index.html",
                user=submission_response_json["account"]["displayName"]
                + " ("
                + submission_response_json["account"]["username"]
                + ")",
                url=origin,
                desc="Image embeds are disabled by this user.",
                site_name=config.get("site_config", "site_name"),
                colour="#" + config.get("site_config", "colour"),
            )

        return render_template(
            "index.html",
            user=submission_response_json["account"]["displayName"]
            + " ("
            + submission_response_json["account"]["username"]
            + ")",
            img="https://submissions.buzzly.art" + submission_response_json["path"],
            url=origin,
            desc=submission_response_json["description"],
            site_name=config.get("site_config", "site_name"),
            colour="#" + config.get("site_config", "colour"),
        )
    return Response(
        "Subpath is not valid",
        status=400,
    )


if __name__ == "__main__":
    app.run(debug=config.getboolean("debug_config", "debug"))
    app.run(
        host=config.get("debug_config", "host"),
        port=config.getint("debug_config", "port"),
    )
