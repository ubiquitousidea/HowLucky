select mp.release_id, 
  rl.title, 
  mp.lowest_price, 
  mp.num_for_sale , 
  mp."when" 
from public.marketplace mp 
left join public.releases rl on rl.release_id = mp.release_id 
order by mp."when" desc limit 50;