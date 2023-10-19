select releases.release_id, artist_by_release.artist_name, artist_by_release.title, releases.format, releases.format_details
from public.releases
join artist_by_release on artist_by_release.release_id = releases.release_id
where releases.format_details is not null and artist_by_release.artist_rank = 0;