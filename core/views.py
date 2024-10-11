from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DeleteView, UpdateView, View, ListView, DetailView
from .models import Category, Staller, MenuItems, Following, Rating, FooRating,Foo_Category,New_offer, Rater, Review, UserLike
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, FriendRequest, CustomUser, EmailVerification
from users.forms import UserSearchForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from .forms import StallerForm,SignInForm, RatingForm, AddItemForm, MenuRatingForm, FooCategoryForm,NewOfferForm,EditOfferForm, CustomUserCreationForm, OTPForm, StallerSurveyForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail  # Import for sending email
from django.utils.crypto import get_random_string 

class Home(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by', '')
        stalls = Staller.objects.all()
        cat = Category.objects.all()
        popu = Staller.objects.filter(Q(category__cat_name__icontains='Popular'))
        item = MenuItems.objects.all()

        if sort_by == 'ratings_high_to_low':
            stalls = stalls.order_by('-rating')
            popu = stalls.order_by('-rating')
        
        elif sort_by == 'ratings_low_to_high':
            stalls = stalls.order_by('rating')
            popu = stalls.order_by('rating')
        elif sort_by == 'followers_high_to_low':
            stalls = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
            popu = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
        elif sort_by == 'followers_low_to_high':
            stalls = sorted(stalls, key=lambda x: x.followers.count())
            popu = sorted(stalls, key=lambda x: x.followers.count())

        # Adding follow_count for each staller
        stalls_with_follow_count = []
        for stall in stalls:
            stall_dict = {
                'stall': stall,
                'follow_count': stall.followers.count()
            }
            stalls_with_follow_count.append(stall_dict)

        popu_stalls_with_follow_count = []
        for popu_stall in popu:
            popu_stall_dict = {
                'popu_stall': popu_stall,
                'follow_count': popu_stall.followers.count()
            }
            popu_stalls_with_follow_count.append(popu_stall_dict)

        context = {
            'stalls_with_follow_count': stalls_with_follow_count,
            'popu_stalls_with_follow_count': popu_stalls_with_follow_count,
            'cat': cat,
            'item': item,
            'popu': popu,
            'sort_by': sort_by,
        }

        return render(request, 'main/index.html', context)


###    EDIT_VIEW     ###
##Staller##
class EditPost(UpdateView):
    model=Staller
    fields=['address', 'contact',
            'timings', 'keywords']
    template_name='edits/editinfo.html'

##Menu-Item##
@login_required
def edit_menu_item(request, item_id):
    staller = get_object_or_404(Staller, owner=request.user)
    menu_item = get_object_or_404(MenuItems, id=item_id, owner__owner=request.user)  # Ensure the user owns the item

    if request.method == 'POST':
        form = AddItemForm(request.POST, request.FILES, instance=menu_item)  # Load the existing item into the form
        if form.is_valid():
            form.save()  # Save the changes
            return redirect('detail', name=menu_item.owner)  # Redirect to the staller's detail page
    else:
        form = AddItemForm(instance=menu_item)  # Load the existing item into the form
        form.fields['foo_cat'].queryset = Foo_Category.objects.filter(sh_owner=staller)

    return render(request, 'edits/edititem.html', {'form': form, 'menu_item': menu_item})
####____USER
from .forms import CustomUserEditForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile', username=request.user.username)  # Redirect to the profile page or wherever you want
    else:
        form = CustomUserEditForm(instance=request.user)

    return render(request, 'edits/edit_user.html', {'form': form}) 


### Add-In-Views ####

###MENU-ITEM###
@login_required 
def add_menu_item(request, staller_id):
    staller = get_object_or_404(Staller, id=staller_id, owner=request.user)
    
    if request.method == 'POST':
        form = AddItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.owner = staller  # Set the owner to the retrieved staller
            menu_item.save()  # Save the menu item to the database
            return redirect('detail', name=staller.name)
    else:
        # Initialize the form and filter the foo_cat field based on the staller
        form = AddItemForm()
        form.fields['foo_cat'].queryset = Foo_Category.objects.filter(sh_owner=staller)

    return render(request, 'add/additem.html', {'form': form, 'staller': staller})


###foo_Category##

@login_required
def add_foo_category(request):
    if request.method == 'POST':
        form = FooCategoryForm(request.POST)
        if form.is_valid():
            foo_category = form.save(commit=False)
            staller = Staller.objects.filter(owner=request.user).first()  # Use first() to get the first instance
            if staller:
                foo_category.sh_owner = staller
                foo_category.save()
                return redirect(reverse('detail', kwargs={'name': staller.name}))  # Redirect to ListView
            else:
                form.add_error(None, 'You must have a Staller profile to add a Foo Category.')
    else:
        form = FooCategoryForm()
    
    return render(request, 'add/add_foo_category.html', {'form': form})


@login_required
def delete_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItems, id=item_id, owner__owner=request.user)  # Ensure the user owns the item
    if request.method == 'POST':
        menu_item.delete()  # Delete the item
        return redirect('detail', name=menu_item.owner)  # Redirect to the staller's detail page
    return render(request, 'confirm_delete.html', {'menu_item': menu_item})

### Detail_View ###
class ListView(DetailView):
    model = Staller
    template_name = 'main/detailview.html'
    context_object_name = 'stall'
    slug_field = 'name'
    slug_url_kwarg = 'name'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staller = self.get_object()
        averages = staller.get_average_survey()
        
        if self.request.user.is_authenticated:
            is_following = Following.objects.filter(user=self.request.user, staller=staller).exists()
            try:
                rating = Rating.objects.get(user=self.request.user, staller=staller)
                form = RatingForm(instance=rating)
            except Rating.DoesNotExist:
                form = RatingForm()

            menu_rating_forms = {}
            for item in staller.menu_items.all():
                try:
                    menu_rating = FooRating.objects.get(user=self.request.user, menu=item)
                    menu_rating_forms[item.id] = MenuRatingForm(instance=menu_rating, prefix=f'menu_{item.id}')
                except FooRating.DoesNotExist:
                    menu_rating_forms[item.id] = MenuRatingForm(prefix=f'menu_{item.id}')
        else:
            is_following = False
            form = None
            menu_rating_forms = {}
        
        users = CustomUser.objects.all()
        category=Category.objects.all()
        context['category']=category
        context['offers']=staller.offers.all()
        context['menu_items'] = staller.menu_items.all()
        context['is_following'] = is_following
        context['follow_count'] = staller.followers.count()
        context['users'] = users
        context['form'] = form
        context['menu_rating_forms'] = menu_rating_forms
        context['staller_rating_count'] = staller.ratings.count()
        menu_rating_counts = {item.id: item.foo_ratings.count() for item in staller.menu_items.all()}
        context['menu_rating_counts'] = menu_rating_counts
        context['averages']=averages
        context['menu_items_by_category'] = {}
        for item in staller.menu_items.all():
            category = item.foo_cat
            if category not in context['menu_items_by_category']:
                context['menu_items_by_category'][category] = []
            context['menu_items_by_category'][category].append(item)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        staller = self.object
        form = RatingForm(request.POST)
        
        if form.is_valid():
            rating, created = Rating.objects.get_or_create(user=request.user, staller=staller)
            rating.rating = form.cleaned_data['rating']
            rating.save()
            staller.update_rating()  # Update the staller's rating
            messages.success(request, 'Rating for staller submitted successfully.')
            return redirect('detail', name=staller.name)
        
        for item in staller.menu_items.all():
            menu_form = MenuRatingForm(request.POST, prefix=f'menu_{item.id}')
            if menu_form.is_valid():
                foo_rating, created = FooRating.objects.get_or_create(user=request.user, menu=item)
                foo_rating.rating = menu_form.cleaned_data['rating']  # Corrected the field name
                foo_rating.save()
                item.update_rating()  # Corrected the method name
                messages.success(request, f'Rating for {item.name} submitted successfully.')
        
        return self.get(request, *args, **kwargs)


#####    LOG_IN,LOG_OUT, REGISTER   #####

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will be activated after OTP verification
            user.save()

            # Generate and save OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')
            EmailVerification.objects.create(user=user, otp=otp)

            # Send OTP via email
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP is {otp}',
                'from@example.com',  # Set your "from" email here
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Account created! Please verify your email by entering the OTP sent.')
            return redirect('verify_otp', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'register/register.html', {'form': form})




def verify_otp(request, user_id):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        otp_entered = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(id=user_id)
            verification = EmailVerification.objects.get(user=user)

            # Correctly access the is_expired property (without parentheses)
            if verification.is_expired:
                messages.error(request, 'OTP has expired.')
                return redirect('resend_otp')

            # Check if the OTP entered matches
            if verification.otp == otp_entered:
                user.is_active = True  # Activate the user after successful OTP
                user.save()
                messages.success(request, 'Your email has been verified successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'No OTP record found for this user.')
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html',{'form': form})


##ADD
def resend_otp_view(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        EmailVerification.objects.update_or_create(user=user, defaults={'otp': otp})

        # Send the new OTP via email
        send_mail(
            'Your OTP Code',
            f'Your new OTP is: {otp}',
            'from@example.com',  # Replace with your sender email
            [user.email],
            fail_silently=False,
        )
        messages.success(request, 'OTP has been resent to your email.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User does not exist.')

    return redirect('verify_otp', user_id=user_id)  



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            user.current_session_key = request.session.session_key
            user.save(update_fields=['current_session_key'])
            auth_hash = user.get_session_auth_hash()

            # Get the next parameter or redirect to 'home'
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

def logout_view(request):
    user = request.user
    if user.is_authenticated:
        user.current_session_key = None
        user.save(update_fields=['current_session_key'])
    auth_logout(request)
    messages.success(request, 'Your are logged out!')
    return redirect('home')




###  FRIEND_REQUEST, Profiles, Owner_profile    ###
def profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    form = UserSearchForm()
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user)
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user)
    followed_stallers = Staller.objects.filter(followers__user=user)
    friends = user.friends.all()

    context={
        'profile_user': user,
        'form': form,
        'friend_requests_sent': friend_requests_sent,
        'friend_requests_received': friend_requests_received,
        'friends': friends,
        'followed_stallers': followed_stallers,
    }
    return render(request, 'profile/profile.html', context)

def user_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followed_stallers = Staller.objects.filter(followers__user=user)
    context={
            'usered': user, 
            'followed_stallers': followed_stallers
            }
    return render(request, 'profile/user_profile.html', context)



@login_required
def send_friend_request(request):
    if request.method == 'POST':
        to_username = request.POST.get('to_user')
        to_user = get_object_or_404(CustomUser, username=to_username)
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('profile', username=request.user.username)

@login_required
def accept_friend_request(request):
    if request.method == 'POST':
        friend_request_id = request.POST.get('request_id')
        friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
        if friend_request.to_user == request.user:
            request.user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(request.user)
            friend_request.delete()
    return redirect('profile', username=request.user.username)

@login_required
def delete_friend_request(request):
    if request.method == 'POST':
        friend_request_id = request.POST.get('request_id')
        friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
        if friend_request.to_user == request.user or friend_request.from_user == request.user:
            friend_request.delete()
    return redirect('profile', username=request.user.username)


###SEARCH_
@login_required
def search_users(request):
    form = UserSearchForm(request.GET)
    results = []
    if form.is_valid():
        results = form.search()
    return render(request, 'search_results.html', {'form': form, 'results': results})

def search(request):
    categor = Category.objects.all()
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')

    if query:
        stallers = Staller.objects.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) | 
            Q(keywords__icontains=query)|
            Q(category__cat_name__icontains=query)
        )

        if sort_by == 'ratings_high_to_low':
            stallers = stallers.order_by('-rating')
        elif sort_by == 'ratings_low_to_high':
            stallers = stallers.order_by('rating')
        elif sort_by == 'followers_high_to_low':
            stallers = sorted(stallers, key=lambda x: x.followers.count(), reverse=True)
        elif sort_by == 'followers_low_to_high':
            stallers = sorted(stallers, key=lambda x: x.followers.count())

        menuitems = MenuItems.objects.filter(
            Q(name__icontains=query) |
            Q(owner__name__icontains=query) |
            Q(foo_cat__foo_name__icontains=query)|
            Q(description__icontains=query)
        )
        menu_rating_counts = {item.id: item.foo_ratings.count() for item in menuitems}
        stalls_with_follow_count = []
        for stall in stallers:
            stall_dict = {
                'stall': stall,
                'follow_count': stall.followers.count()
            }
            stalls_with_follow_count.append(stall_dict)
    else:
        stallers = Staller.objects.none()
        menuitems = MenuItems.objects.none()
        menu_rating_counts = {}

    context = {
        'stallers': stallers,
        'menuitems': menuitems,
        'menu_rating_counts': menu_rating_counts,
        'query': query,
        'stalls_with_follow_count': stalls_with_follow_count,
        'categor': categor,
        'sort_by': sort_by,
    }

    return render(request, 'search.html', context)




###((((STALL FOLLOWING))))####


class FollowStallerView(LoginRequiredMixin, View):
    def post(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        Following.objects.get_or_create(user=request.user, staller=staller)
        return redirect('detail', name=staller.name)

class UnfollowStallerView(LoginRequiredMixin, View):
    def post(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        Following.objects.filter(user=request.user, staller=staller).delete()
        return redirect('detail', name=staller.name)
    




def future(request):
    return render(request,'main/future.html')

class OfferView(View):
    def get(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        offers = staller.offers.order_by('-last_updated')
        context = {
            'staller': staller,
            'offers': offers,
        }
        return render(request, 'offers.html', context)
    

class NewOfferView(View):
    def get(self, request, staller_name):
        staller = get_object_or_404(Staller, name=staller_name)
        if staller.owner != request.user:
            return redirect('home')
        form = NewOfferForm()
        return render(request, 'add/new_offer.html', {'form': form, 'staller': staller})

    def post(self, request, staller_name):
        staller = get_object_or_404(Staller, name=staller_name)
        if staller.owner != request.user:
            return redirect('home')
        form = NewOfferForm(request.POST, request.FILES)
        if form.is_valid():
            new_offer = form.save(commit=False)
            new_offer.owner = staller
            new_offer.save()
            return redirect('offers', name=staller.name)
        return render(request, 'new_offer.html', {'form': form, 'staller': staller})
    
class EditOfferView(View):
    def get(self, request, offer_id):
        offer = get_object_or_404(New_offer, id=offer_id)
        if offer.owner.owner != request.user:
            return redirect('home')
        form = EditOfferForm(instance=offer)
        return render(request, 'edits/edit_offer.html', {'form': form, 'offer': offer})

    def post(self, request, offer_id):
        offer = get_object_or_404(New_offer, id=offer_id)
        if offer.owner.owner != request.user:
            return redirect('home')
        form = EditOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offers', name=offer.owner.name)
        return render(request, 'edits/edit_offer.html', {'form': form, 'offer': offer})

@login_required
def delete_offer(request, offer_id):
    offer = get_object_or_404(New_offer, id=offer_id)
    if offer.owner.owner != request.user:
        return redirect('home')

    if request.method == 'POST':
        offer.delete()
        return redirect('offers', name=offer.owner.name)
    
    return render(request, 'delete_offer.html', {'offer': offer})

def cat_view(request, foo):
    categor = Category.objects.get(cat_name=foo)
    stalls = Staller.objects.filter(category=categor)
    sort_by = request.GET.get('sort_by', '')
    category = Category.objects.all()


    if sort_by == 'ratings_high_to_low':
        stalls = stalls.order_by('-rating')
    elif sort_by == 'ratings_low_to_high':
        stalls = stalls.order_by('rating')
    elif sort_by == 'followers_high_to_low':
        stalls = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
    elif sort_by == 'followers_low_to_high':
        stalls = sorted(stalls, key=lambda x: x.followers.count())


    stalls_with_follow_count = []
    for stall in stalls:
        stall_dict = {
            'stall': stall,
            'follow_count': stall.followers.count()
        }
        stalls_with_follow_count.append(stall_dict)

    context = {
        'stalls_with_follow_count': stalls_with_follow_count,
        'stalls': stalls,
        'categor': categor,
        'category': category,
        'sort_by': sort_by,
    }

    return render(request, 'category.html', context)


from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)


# Reset_Password
from django.contrib.auth.views import PasswordResetView

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'register/custom_password_reset_email.html'
    def get_email_options(self):
        options = super().get_email_options()
        # Set your custom domain here
        options['domain'] = 'https://www.assanj.in/'
        return options


from django.http import JsonResponse
# Rater


def like_rater(request, rater_id):
    rater = get_object_or_404(Rater, id=rater_id)
    if request.user in rater.likes.all():
        rater.likes.remove(request.user)
        liked = False
    else:
        rater.likes.add(request.user)
        liked = True

    return JsonResponse({'total_likes': rater.total_likes(), 'liked': liked})


def review_rater(request, rater_id):
    rater = get_object_or_404(Rater, id=rater_id)
    rating = int(request.POST.get('rating', 0))
    review, created = Review.objects.get_or_create(user=request.user, rater=rater)
    review.rating = rating
    review.save()

    return JsonResponse({'average_rating': rater.average_rating(), 'user_rating': review.rating})


def rater_list(request):
    sort_by = request.GET.get('sort_by', 'likes')  # Default sort by likes
    if sort_by == 'likes':
        raters = Rater.objects.annotate(
            like_count=Count('likes'),
            avg_rating=Avg('review__rating')
        ).order_by('-like_count', '-avg_rating')
    elif sort_by == 'ratings':
        raters = Rater.objects.annotate(
            like_count=Count('likes'),
            avg_rating=Avg('review__rating')
        ).order_by('-avg_rating', '-like_count')

    context = {
        'raters': raters,
        'sort_by': sort_by
    }
    return render(request, 'rater_list.html', context)


from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

@login_required  # Ensure this view is only accessible by logged-in users
def like_staller(request, staller_id):
    staller = get_object_or_404(Staller, id=staller_id)
    
    # Check if the user already liked this staller
    if UserLike.objects.filter(user=request.user, staller=staller).exists():
        return JsonResponse({'error': 'You have already liked.'}, status=400)

    # Increment the like count
    staller.likes += 1
    staller.save()

    # Record the like in the UserLike model
    UserLike.objects.create(user=request.user, staller=staller)

    return JsonResponse({'likes': staller.likes})





def staller_survey(request, staller_id):
    staller = get_object_or_404(Staller, id=staller_id)
    
    if request.method == 'POST':
        form = StallerSurveyForm(request.POST, instance=staller)
        if form.is_valid():
            form.save()

            # Increment user points by 5 after form submission
            if request.user.is_authenticated:
                request.user.points += 5
                request.user.save()

            return redirect('detail', staller.name)  # Redirect to the staller detail page
    else:
        form = StallerSurveyForm(instance=staller)

    return render(request, 'staller_survey.html', {'form': form, 'staller': staller})
