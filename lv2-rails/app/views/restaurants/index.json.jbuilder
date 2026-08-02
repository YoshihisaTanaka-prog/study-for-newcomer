json.restaurants @restaurants do |restaurant|
  json.partial! "restaurants/restaurant", restaurant:
end
