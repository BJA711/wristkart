from django.urls import path,include
from . import views
urlpatterns=[
    path('',views.hp),
    path('h/',views.hp),
    path('sap/',views.showadminpage),
    path('adp/',views.addproduct),
    path('ap/',views.listproduct),
    path('del/<int:id>/',views.delprogram),
    path('ed/<int:id>/',views.editproduct),

    path('profile/', views.profile),
    path('pp/',views.registration),
    path('bb/',views.login),
    path('atoc/<int:id>/',views.order),
    path('vc/', views.viewcart),
    path('delp/<int:id>/', views.removeitem),
    path('pay/', views.payment),
    path('upay/', views.userpayment),
    path('logout/', views.logout),
    path('product/<int:id>/', views.product_detail),
    path('updateqty/<int:id>/<str:action>/', views.updateqty),
    path('category/<str:cat>/', views.category_page),



    path('passs/', views.changepassword),
    path('myp/', views.viewsales),
    path('ms/<int:salesno>/', views.viewsalessub),


    path('inv/', views.adminviewsales),
    path('invoice/<int:salesno>/', views.invoice_view),
    path('search/', views.search_products),



    path('adms/',views.adminsaleshistory),

]