import dropbox
import os
from django.conf import settings

# Dropbox configuration
DROPBOX_ACCESS_TOKEN = "sl.u.AGF_eDv5BUVJ6zrhSd6IzYMm4yDX-KqEUfCkFofqB6VmuFIXuclJJ_HAEdR7WODbuoD5Bwvypzs9fVuIJvxr2kkrDdJ987CrdGZ2kxzxRFAEVzaIarKC0zy4PggI-6_YdXbxkr1kuWdYVq-eLnJ6AgBbN9KPdKZ0SPvpZrD7XnkW_WRMOwkbJzEwSBUnswNOrTtMhaG-weluDgAKk5GDyduWc9Q5uOKAgiZpIUl8trPelobseoutmCQODcQaFYhjd1O4qn8tmKwpro2o6NV3fOiJZra7fzQVF2RepC-CDG1lMFLiuJJXifeqyAo5CgzdisJlMexPk_qGdnd8ZxnugyXexVg0ABhlD9OpXqvo_zV9mgjoL8NOhN5wEYhLqYyVluveDjV1QMixM0IYBBubMIbgrEJzC6KmpfgibOJRU9WMUlZiF42bnTJqJ-QdBaDpDTuWWVYeFi6OGNi7nEkWokSmBijKLPeNbm5CuRqz95SbQzi_BO5PilSv2xt4N5MKgRbA76eT-hEp9DkFmWUHvQ7sa4ZSZEBLoE533nRvXxGd4valvJGuj6f_-k1YeKUsKnq-lqXc417gT6aZs855tQc6rh6WIqM3hyQFrNCyCD312fLNkE5I6NS0vafzH_2DvIMqIMe-y1U5VHAhQMWvZJLY1SuZk_dGQEx4tgiwNJ7pdyVzx2Mx2Zf7lXMG-SUA7MIUW04IEuRgoQcKwKovyHpQQqiHW1CBbvRxOqDkGnFX1JEXFsXgfksW4cBK0kPjZ5VO-eBFeadxxiEu2HsN5HB1d1uHUND6LRqhjxh1w0YILQtkugxe-hoDb0I-K52LIwlAzlTCvjR0Mrtsvk9U1gEm3IVVu_OutMb3xF3CG2ag48dJa0tE8vdOAc0FodlczbXDY8N17UuWhjpBnLiTc3SZ87e1_8hiSvqeSzgGnQP68XJDf-BFfvQ0cBLtBnz-KOie0X4vzk6q54Xy4UB4YO6YwefU_j4wSA4mbTUWQfw4MxgQqwidGvIaiVjegWvx8hQcgQnPmkBjVG51yE1kJZE7aRkZSH6W5rV_igpkIbFKAgzT1EtpRoymT12GnoYAMazhXgKmvlf8JqXTDeGtQri1vqQqMy8rT-a1m5qYi0C7RR94EvThUt12HLOBjW8gKw7_7vG2_Dt1N3HEj7nPiXHC8Us93tWBCVUbClIZlHpEoZkisklXIbEyvYYbuHoDdCV3f6Nv1Px5whunjBJWIy3n9BzadsHryYN5zob7mF6KbySJcLmlBNtv5U8RSW4lzuzsqCxvJ3_qk9ua95OFOO8V"

def get_direct_dropbox_link(shared_url):
    """Convert Dropbox shared link to direct link."""
    if "dropbox.com" in shared_url:
        shared_url = shared_url.replace("?dl=0", "?raw=1")
        shared_url = shared_url.replace("?dl=1", "?raw=1")
        shared_url = shared_url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
    return shared_url

def upload_devotee_photo(photo_file, devotee_data):
    """Upload devotee photo to Dropbox and return direct URL."""
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        
        # Create filename from devotee data: first_last_number
        name_parts = devotee_data['name'].strip().split()
        first_name = name_parts[0].lower() if name_parts else 'unknown'
        last_name = name_parts[-1].lower() if len(name_parts) > 1 else ''
        contact_number = devotee_data.get('contact_number', '0000000000')
        
        file_extension = os.path.splitext(photo_file.name)[1] or '.jpg'
        filename = f"{first_name}_{last_name}_{contact_number}{file_extension}" if last_name else f"{first_name}_{contact_number}{file_extension}"
        dropbox_path = f"/devotee_photos/{filename}"
        
        # print(f"Uploading photo as: {filename}")
        
        # Reset file pointer to beginning
        photo_file.seek(0)
        file_content = photo_file.read()
        
        # Upload file
        upload_result = dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        # print(f"Upload successful: {upload_result.name}")
        
        # Create shared link
        try:
            link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        except dropbox.exceptions.ApiError:
            # Link already exists
            links = dbx.sharing_list_shared_links(path=dropbox_path).links
            link = links[0] if links else None
        
        if link:
            direct_url = get_direct_dropbox_link(link.url)
            # print(f"Direct URL: {direct_url}")
            return direct_url
        
        return None
        
    except Exception as e:
        print(f"Dropbox upload error: {e}")
        return None