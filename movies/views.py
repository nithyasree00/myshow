from django.db.models import Q
from .models import BookingHistory 
from django.utils.timezone import localdate
from ntpath import join
 # Add this at the top of views.py



from django.shortcuts import render, redirect ,get_object_or_404 # type: ignore
from .models import Movie,Theater,Seat,Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

def movie_list(request):
    search_query=request.GET.get('search')
    if search_query:
        movies=Movie.objects.filter(name__icontains=search_query)
    else:
        movies=Movie.objects.all()
    return render(request,'movies/movie_list.html',{'movies':movies})

def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

@login_required(login_url='/login/')
def book_seats(request,theater_id):
    theaters=get_object_or_404(Theater,id=theater_id)
    seats=Seat.objects.filter(theater=theaters)
    if request.method=='POST':
        selected_Seats= request.POST.getlist('seats')
        error_seats=[]
        if not selected_Seats:
            return render(request,"movies/seat_selection.html",{'theaters':theaters,"seats":seats})
        for seat_id in selected_Seats:
            seat=get_object_or_404(Seat,id=seat_id,theater=theaters)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theaters.movie,
                    theater=theaters
                )
                BookingHistory.objects.create(
                    user=request.user,
                    genre=theaters.movie.genre
                )
                


                seat.is_booked=True
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)
        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"

            return render(request,'movies/seat_selection.html',{'theaters':theaters,"seats":seats,'error':"No seat selected"})
        return redirect('profile')
    return render(request,'movies/seat_selection.html',{'theaters':theaters,"seats":seats})


def home(request):
    today = localdate()
    todays_shows = Theater.objects.filter(date=today).select_related('movie')

    unique_movies = Movie.objects.filter(
        id__in=todays_shows.values_list('movie_id', flat=True).distinct()
    )

    recommended_movies = []
    print("User authenticated?", request.user.is_authenticated)

    if request.user.is_authenticated:
        booked_genres = BookingHistory.objects.filter(user=request.user).values_list('genre', flat=True)
        booked_movies = Booking.objects.filter(user=request.user).values_list('movie_id', flat=True)
        print(" Genres you booked:", booked_genres)
        print(" Movies you booked:", booked_movies)
        
    
        recommended_movies = Movie.objects.filter(
            genre__in=booked_genres
        ).exclude(id__in=booked_movies).distinct()
        
        print(" Final recommended list:", recommended_movies)


    context = {
        'unique_movies': unique_movies,
        'recommended_movies': recommended_movies
    }
    return render(request, 'home.html', context)

    





