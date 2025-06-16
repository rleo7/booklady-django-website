from .models import Badge

def check_for_new_badges(user):
    new_badges = []
    for badge in Badge.objects.all():
        if badge.target_books and user.lifetime_books_read >= badge.target_books:
            if badge not in user.badges.all():
                user.badges.add(badge)
                new_badges.append(badge)
        elif badge.target_pages and user.lifetime_pages_read >= badge.target_pages:
            if badge not in user.badges.all():
                user.badges.add(badge)
                new_badges.append(badge)
    return new_badges