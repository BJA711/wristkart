from django.shortcuts import render,redirect
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.db.models import Max,Value
from django.db.models import F
from datetime import date
from  myapp.models import product,usreg,cart,onlinemaster,onlinesub
import random
from django.http import HttpResponse

from django.shortcuts import get_object_or_404


def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'id' not in request.session:
            return redirect('/bb/')
        return view_func(request, *args, **kwargs)
    return wrapper

@user_required
def invoice_view(request, salesno):
    master = get_object_or_404(onlinemaster, salesno=salesno)
    items = onlinesub.objects.filter(salesno=salesno)
    return render(request, "invoice.html", {
        "master": master,
        "items": items
    })


def logout(request):
    request.session.flush()
    return redirect('/')


def hp(request):
    smart = product.objects.filter(category='smart')[:4]
    luxury = product.objects.filter(category='luxury')[:4]
    sport = product.objects.filter(category='sport')[:4]
    casual = product.objects.filter(category='casual')[:4]
    popular = product.objects.all()[:4]
    cart_count = 0
    if 'id' in request.session:
        cart_count = cart.objects.filter(userid=request.session['id']).count()
    return render(request, "homepage.html", {
        "smart": smart,
        "luxury": luxury,
        "sport": sport,
        "casual": casual,
        "popular": popular,
        "cart_count": cart_count
    })


def product_detail(request, id):
    try:
        prod = product.objects.get(id=id)
    except product.DoesNotExist:
        return redirect('/')
    return render(request, "productdetail.html", {"prod": prod})


@user_required
def updateqty(request, id, action):
    item = cart.objects.filter(id=id, userid=request.session['id']).first()
    if not item:
        return redirect('/vc/')
    if action == "inc":
        item.qty += 1
    elif action == "dec":
        item.qty -= 1
        if item.qty <= 0:
            item.delete()
            return redirect('/vc/')
    # Recalculate total
    item.total = item.qty * item.rate
    item.save()
    return redirect('/vc/')


# Create your views here.
def addproduct(request):
    if request.method == "POST":
        mpcode = request.POST.get('pcode')
        mpname = request.POST.get('pname')
        mbrand = request.POST.get('brand')
        mcategory = request.POST.get('category')
        mgender = request.POST.get('gender')
        mstrap = request.POST.get('strap')
        mfile = request.FILES['file']
        mprice = request.POST.get('price')
        mstock = request.POST.get('stock')
        pa = product(
            tpcode=mpcode,
            tpname=mpname,
            brand=mbrand,
            category=mcategory,
            gender=mgender,
            strap_material=mstrap,
            tfile=mfile,
            tprice=mprice,
            tstock=mstock
        )
        pa.save()
        return redirect("/sap/")
    return render(request, "adminaddproduct.html")


def listproduct(request):
    crec=product.objects.all()
    return render(request, "adminlistproduct.html",{"crec":crec})


def delprogram(request,id):
    product.objects.filter(id=id).delete()
    return redirect("/ap/")


def editproduct(request, id):
    if request.method == "POST":
        mpcode = request.POST.get('pcode')
        mpname = request.POST.get('pname')
        mbrand = request.POST.get('brand')
        mcategory = request.POST.get('category')
        mgender = request.POST.get('gender')
        mstrap = request.POST.get('strap')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        product.objects.filter(id=id).update(
            tpcode=mpcode,
            tpname=mpname,
            brand=mbrand,
            category=mcategory,
            gender=mgender,
            strap_material=mstrap,
            tprice=price,
            tstock=stock
        )
        return redirect("/ap/")
    mrec = product.objects.get(id=id)
    return render(request, "admineditproduct.html", {"mrec": mrec})


@user_required
def profile(request):
    user = usreg.objects.get(id=request.session['id'])
    orders = onlinemaster.objects.filter(userid=request.session['id'])
    return render(request, "profile.html", {
        "user": user,
        "orders": orders
    })


def registration(request):
    if request.method == "POST":
        fn = request.POST.get('fn')
        email = request.POST.get('email')
        phone = request.POST.get('phoneno')
        username = request.POST.get('un')
        password = request.POST.get('psw')
        confirm = request.POST.get('cpws')
        if password != confirm:
            return render(request, "registration.html", {
                "error": "Passwords do not match."
            })
        if usreg.objects.filter(un=username).exists():
            return render(request, "registration.html", {
                "error": "Username already exists."
            })
        if usreg.objects.filter(email=email).exists():
            return render(request, "registration.html", {
                "error": "Email already registered."
            })
        usreg.objects.create(
            fn=fn,
            email=email,
            phoneno=phone,
            un=username,
            psw=password,
            cpws=confirm
        )
        return redirect("/bb/")
    return render(request, "registration.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get('un')
        password = request.POST.get('psw')
        if not username or not password:
            return render(request, "login.html", {"error": "All fields are required."})
        user = usreg.objects.filter(un=username, psw=password)
        if user.exists():
            u = user.first()
            request.session['id'] = u.id
            request.session['name'] = u.fn
            request.session['uname'] = u.un
            request.session['right'] = u.rights
            if u.rights == "admin":
                return redirect("/sap/")
            else:
                return redirect("/")
        else:
            return render(request, "login.html", {"error": "Invalid username or password."})
    return render(request, "login.html")


def showadminpage(request):
    total_products = product.objects.count()
    total_orders = onlinemaster.objects.count()
    total_users = usreg.objects.count()
    total_revenue = onlinemaster.objects.aggregate(
        total=Sum('total')
    )['total'] or 0
    return render(request, "adminpage.html", {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue
    })


@user_required
def order(request,id):
    mrec=product.objects.filter(id=id)
    for j in mrec:
        fname=j.tpname
        price=j.tprice
        qty=j.tstock
        photo=j.tfile
    qts=[]
    for j in range(1,qty+1):
        qts.append(j)
    if request.method=="POST":
            oq=request.POST.get('qtys')
            tot=int(oq)* price
            ca = cart(
                slno=id,
                pname=fname,
                rate=price,
                qty=oq,
                total=tot,
                userid=request.session['id']
            )
            ca.save()
            return redirect("/vc/")
    return render(request, "userpurchase.html",{"fname":fname,"price":price,"qts":qts,"photo":photo})


@user_required
def viewcart(request):
    cart_items = cart.objects.filter(userid=request.session['id'])
    data = []
    total_amount = 0
    for item in cart_items:
        prod = product.objects.filter(id=item.slno).first()
        if prod:
            image = prod.tfile.url
        else:
            image = None
        data.append({
            "id": item.id,
            "pname": item.pname,
            "rate": item.rate,
            "qty": item.qty,
            "image": image
        })
        total_amount += item.total
    return render(request, "vieworder.html", {
        "data": data,
        "total": total_amount
    })


@user_required
def removeitem(request, id):
    cart.objects.filter(id=id, userid=request.session['id']).delete()
    return redirect('/vc/')


@user_required
def payment(request):
    cart_items = cart.objects.filter(userid=request.session['id'])
    if not cart_items:
        return redirect('/vc/')
    total_amount = 0
    for item in cart_items:
        total_amount += item.total
    if request.method == "POST":
        return redirect('/upay/')
    return render(request, "payment.html", {
        "cart_items": cart_items,
        "total": total_amount,
        "name": request.session['name']
    })


@user_required
def userpayment(request):
    fullname = request.POST.get("fullname")
    phone = request.POST.get("phone")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    pincode = request.POST.get("pincode")
    payment_method = request.POST.get("payment_method")
    account = request.POST.get("account_number")
    if request.method != "POST":
        return redirect('/vc/')
    cart_items = cart.objects.filter(userid=request.session['id'])
    if not cart_items:
        return redirect('/vc/')
    address = request.POST.get("address")
    account = request.POST.get("account_number")
    total_amount = 0
    for item in cart_items:
        total_amount += item.total
    # Generate new sales number
    max_salesno = onlinemaster.objects.aggregate(
        max_salesno=Coalesce(Max('salesno'), Value(0))
    )['max_salesno']
    new_salesno = int(max_salesno) + 1
    # Create master order
    master = onlinemaster(
        salesno=new_salesno,
        userid=request.session['id'],
        uname=fullname,
        shipment=f"{address}, {city}, {state} - {pincode}",
        phone=phone,
        cardno=account[-4:] if account else "COD",
        total=total_amount,
        status='New Order'
    )
    master.save()
    slno = 1
    for item in cart_items:
        # Create sub order entries
        onlinesub.objects.create(
            salesno=new_salesno,
            slno=slno,
            pname=item.pname,
            rate=item.rate,
            qty=item.qty,
            total=item.total
        )
        # Reduce stock safely
        product.objects.filter(id=item.slno).update(
            tstock=F('tstock') - item.qty
        )
        slno += 1
    # Clear cart
    cart.objects.filter(userid=request.session['id']).delete()
    # Show animated success page
    return render(request, "ordersuccess.html", {
        "salesno": new_salesno
    })


@user_required
def download_invoice(request, salesno):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{salesno}.pdf"'
    p = canvas.Canvas(response)
    master = onlinemaster.objects.get(salesno=salesno)
    items = onlinesub.objects.filter(salesno=salesno)
    y = 800
    p.drawString(50, y, f"WristKart Invoice")
    y -= 30
    p.drawString(50, y, f"Order #: {salesno}")
    y -= 20
    p.drawString(50, y, f"Customer: {master.uname}")
    y -= 20
    p.drawString(50, y, f"Phone: {master.phone}")
    y -= 20
    p.drawString(50, y, f"Address: {master.shipment}")
    y -= 40
    for item in items:
        p.drawString(50, y, f"{item.pname}  x{item.qty}  -  ${item.total}")
        y -= 20
    y -= 20
    p.drawString(50, y, f"Total Amount: ${master.total}")
    p.showPage()
    p.save()
    return response


@user_required
def invoice_view(request, salesno):
    master = onlinemaster.objects.get(salesno=salesno)
    items = onlinesub.objects.filter(salesno=salesno)
    return render(request, "invoice.html", {
        "master": master,
        "items": items
    })


@user_required
def changepassword(request):
    if request.method == "POST":
        oldpass = request.POST.get("old")
        newpass = request.POST.get("n1")
        confirm = request.POST.get("n2")
        user = usreg.objects.get(id=request.session['id'])
        # Check old password
        if user.psw != oldpass:
            return render(request, "changepass.html", {
                "error": "Old password is incorrect."
            })
        # Check match
        if newpass != confirm:
            return render(request, "changepass.html", {
                "error": "New passwords do not match."
            })
        # Update password
        user.psw = newpass
        user.cpws = newpass
        user.save()
        return render(request, "changepass.html", {
            "success": "Password changed successfully."
        })
    return render(request, "changepass.html")



@user_required
def viewsales(request):
    orders = onlinemaster.objects.filter(
        userid=request.session['id']
    ).order_by('-salesno')
    order_data = []
    for order in orders:
        items = onlinesub.objects.filter(salesno=order.salesno)
        product_list = []
        for item in items:
            prod = product.objects.filter(tpname=item.pname).first()
            if prod:
                image = prod.tfile.url
            else:
                image = None
            product_list.append({
                "name": item.pname,
                "qty": item.qty,
                "price": item.rate,
                "image": image
            })
        order_data.append({
            "salesno": order.salesno,
            "total": order.total,
            "status": order.status,
            "shipment": order.shipment,
            "products": product_list
        })
    return render(request, "mysales.html", {
        "orders": order_data
    })


def category_page(request, cat):
    products = product.objects.filter(category=cat)
    # Cart count (for navbar if needed)
    cart_count = 0
    if 'id' in request.session:
        cart_count = cart.objects.filter(userid=request.session['id']).count()
    return render(request, "category.html", {
        "products": products,
        "category": cat.capitalize(),
        "cart_count": cart_count
    })


def viewsalessub(request,salesno):
    mrec= onlinesub.objects.filter(salesno=salesno)
    return render(request, "mysalessub.html", {"mrec": mrec})


def adminviewsales(request):
    mrec= onlinemaster.objects.filter(status='New Order')
    return render(request, "admininvoice.html", {"mrec": mrec})


def invoice(request,salesno):
    onlinemaster.objects.filter(salesno=salesno).update(status='Invoice')
    return redirect("/sap/")


def adminsaleshistory(request):
    mrec= onlinemaster.objects.all()
    return render(request, "adminsales.html", {"mrec": mrec})

from django.db.models import Q
def search_products(request):
    query = request.GET.get('q')
    products = []
    if query:
        products = product.objects.filter(
            Q(tpname__icontains=query) |
            Q(brand__icontains=query)
        )
    return render(request, "search.html", {
        "products": products,
        "query": query
    })

import os
from django.http import HttpResponse
from django.conf import settings

def test_media(request):
    path = os.path.join(
        settings.MEDIA_ROOT,
        "images",
        "WhatsApp_Image_2026-03-01_at_8.08.36_PM.jpeg"
    )

    return HttpResponse(
        f"Exists: {os.path.exists(path)}<br>Path: {path}"
    )
