json.extract! restaurant,
              :id,
              :name,
              :genre,
              :tabelog_url,
              :price_min,
              :price_max,
              :memo,
              :created_at,
              :updated_at

json.price_label restaurant.price_label

json.office do
  json.extract! restaurant.office, :id, :name, :address
end

json.payment_methods restaurant.payment_methods do |payment_method|
  json.extract! payment_method, :id, :name
end
