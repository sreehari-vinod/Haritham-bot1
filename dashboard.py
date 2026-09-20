from flask import Flask, render_template, request, redirect, url_for

from app.database import (
    get_todays_list,
    update_veg_list,
    get_all_active_customers,
    get_todays_orders
)
app = Flask(__name__)



@app.route("/admin")
def dashboard():

    vegetables = get_todays_list() or {"items": []}
    orders = get_todays_orders()
    customers = get_all_active_customers()

    total_orders = len(orders)
    total_customers = len(customers)
    total_products = len(vegetables["items"])

    today_sales = 0

    return render_template(
        "dashboard.html",
        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products,
        today_sales=today_sales,
        vegetables=vegetables,
        orders=orders,
        customers=customers
    )


# ADD VEGETABLE
@app.route("/admin/add-vegetable", methods=["GET", "POST"])
def add_vegetable():

    vegetables = get_todays_list() or {"items": []}

    if request.method == "POST":

        items = vegetables["items"]

        items.append({
            "name": request.form["name"],
            "price": int(request.form["price"]),
            "unit": request.form["unit"]
        })

        update_veg_list(items)

        return redirect(url_for("dashboard"))

    return render_template("vegetables.html")


# EDIT VEGETABLE
# EDIT VEGETABLE
@app.route("/admin/edit-vegetable/<int:index>", methods=["GET", "POST"])
def edit_vegetable(index):

    vegetables = get_todays_list() or {"items": []}
    items = vegetables["items"]

    if index >= len(items):
        return redirect(url_for("dashboard"))

    veg = items[index]

    if request.method == "POST":

        items[index] = {
            "name": request.form["name"],
            "price": int(request.form["price"]),
            "unit": request.form["unit"]
        }

        update_veg_list(items)

        return redirect(url_for("dashboard"))

    return render_template(
        "edit_vegetable.html",
        veg=veg
    )

    if request.method == "POST":

        veg["name"] = request.form["name"]
        veg["price"] = int(request.form["price"])
        veg["unit"] = request.form["unit"]

        return redirect(url_for("dashboard"))

    return render_template(
        "edit_vegetable.html",
        veg=veg,
        index=index
    )


# DELETE VEGETABLE
@app.route("/admin/delete-vegetable/<int:index>")
def delete_vegetable(index):

    vegetables = get_todays_list() or {"items": []}
    items = vegetables["items"]

    if index < len(items):
        items.pop(index)
        update_veg_list(items)

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)