json.review do
  json.extract! @review, :id, :restaurant_id, :body, :rating, :visited_on, :created_at, :updated_at
end
