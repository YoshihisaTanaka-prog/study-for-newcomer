json.restaurant do
  json.partial! "restaurants/restaurant", restaurant: @restaurant

  json.reviews @restaurant.reviews.order(created_at: :desc) do |review|
    json.extract! review, :id, :body, :rating, :visited_on, :created_at, :updated_at
  end
end
