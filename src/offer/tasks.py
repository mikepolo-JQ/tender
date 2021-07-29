import json

from celery import shared_task
from project.celery import app
from dynaconf import settings as _ds
import requests

from offer.models import Offer, Store, Category, Type

file_name = "data.json"


@app.task
def upload_data_from_file_to_the_db():
    count = 0
    added = 0

    with open(file_name) as data_file:
        data = json.load(data_file)

    offers_data = data.get("offers")

    if not offers_data:
        return KeyError("Can't find offers data...")

    for offer_data in offers_data:

        count += 1

        offer = Offer.objects.filter(lmd_id=offer_data["lmd_id"]).first()

        if offer:
            continue

        # adding stores
        store_name = offer_data["store"]

        store = Store.objects.filter(name=store_name).first()

        if not store:
            store = Store.objects.create(name=store_name)

        # creature offers
        offer = Offer.objects.create(
            lmd_id=offer_data["lmd_id"],
            store=store,
            offer_text=offer_data["offer_text"],
            offer_value=offer_data["offer_value"],
            description=offer_data["description"],
            code=offer_data["code"] if offer_data["code"] else None,
            title=offer_data["title"],
            featured=(False if offer_data["featured"] == "No" else True),
            url=offer_data["url"],
            smart_link=offer_data["smartLink"],
            image_url=offer_data["image_url"],
            status=offer_data["status"],
            start_date=offer_data["start_date"],
            end_date=offer_data["end_date"],
        )

        # adding categories
        categories = offer_data["categories"].split(",")

        for category_name in categories:
            category = Category.objects.filter(name=category_name).first()

            if not category:
                category = Category.objects.create(name=category_name)

            offer.categories.add(category)

        # adding types
        types = [offer_data["type"], offer_data["offer"]]

        for type_name in types:
            type_obj = Type.objects.filter(name=type_name).first()

            if not type_obj:
                type_obj = Type.objects.create(name=type_name)

            offer.types.add(type_obj)

        added += 1

    return json.dumps({"ok": True, "count": count, "added": added})


@app.task
def update_data_file():

    url = "https://linkmydeals.p.rapidapi.com/getOffers/"

    querystring = {
        "API_KEY": _ds.API_KEY,
        "format": "json",
        "incremental": "{incremental}",
        "last_extract": "{last_extract}",
        "off_record": "{off_record}",
    }

    headers = {
        "x-rapidapi-key": _ds.X_RAPIDAPI_KEY,
        "x-rapidapi-host": "linkmydeals.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()

    with open(file_name, "w") as data_file:
        json.dump(response, data_file, indent=4)

    return {"ok": True, "uploaded_count": len(response["offers"])}
