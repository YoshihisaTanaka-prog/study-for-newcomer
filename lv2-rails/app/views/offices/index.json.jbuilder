json.offices @offices do |office|
  json.extract! office, :id, :name, :address
end
