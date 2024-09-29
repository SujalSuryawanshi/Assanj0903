from django.contrib import admin
from django.urls import path, include
from .views import Home,login_view, logout_view,send_friend_request, accept_friend_request, delete_friend_request,ListView,FollowStallerView,UnfollowStallerView,register,cat_view, resend_otp_view
from .views import EditPost,add_menu_item, delete_menu_item, edit_menu_item,future,add_foo_category,OfferView, NewOfferView, EditOfferView, delete_offer, like_rater, review_rater, rater_list, edit_profile
from . import views
urlpatterns = [
    path("",Home.as_view(), name='home' ),
    path('register/', views.register, name='register'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<int:user_id>/', resend_otp_view, name='resend_otp'),
    path("place/<slug:name>/", ListView.as_view(), name="detail"),
    path('accounts/login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search', views.search , name='search'),
    path('search/', views.search_users, name='search_users'),
    path('send_request/', views.send_friend_request, name='send_friend_request'),
    path('accept_request/', views.accept_friend_request, name='accept_friend_request'),
    path('delete_request/', views.delete_friend_request, name='delete_friend_request'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit/<int:pk>',EditPost.as_view() , name='edit_info'),
    path('stallers/<str:name>/follow/', FollowStallerView.as_view(), name='follow_staller'),
    path('stallers/<str:name>/unfollow/', UnfollowStallerView.as_view(), name='unfollow_staller'),
    path('profile/look/<str:username>/', views.user_profile, name='user_profile'),
    path('staller/<int:staller_id>/add_menu_item/', add_menu_item, name='add_menu_item'),
    path('delete-menu-item/<int:item_id>/', delete_menu_item, name='delete_menu_item'),
    path('edit-menu-item/<int:item_id>/', edit_menu_item, name='edit_menu_item'),
    path("future/", views.future, name="future"),
    path('add-foo-category/', add_foo_category, name='add_foo_category'),
    path('stall/<slug:name>/offers/', OfferView.as_view(), name='offers'),
    path('stall/<slug:staller_name>/new_offer/', NewOfferView.as_view(), name='new_offer'),
    path('offer/<int:offer_id>/edit/', EditOfferView.as_view(), name='edit_offer'),
    path('offer/<int:offer_id>/delete/', delete_offer, name='delete_offer'),
    path("category/<str:foo>/", views.cat_view, name="category"),
    path('rater/', views.rater_list, name='rater_list'),
    path('like/<int:rater_id>/', views.like_rater, name='like_rater'),
    path('review/<int:rater_id>/', views.review_rater, name='review_rater'),
    path('edit-profile/', edit_profile, name='edit_profile'),


    ]
