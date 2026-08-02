json.payment_methods @payment_methods do |payment_method|
  json.extract! payment_method, :id, :name
end
