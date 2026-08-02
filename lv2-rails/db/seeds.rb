[
  ["東京本社", "東京都千代田区"],
  ["大阪オフィス", "大阪府大阪市"],
  ["福岡オフィス", "福岡県福岡市"]
].each do |name, address|
  Office.find_or_create_by!(name:) do |office|
    office.address = address
  end
end

[
  "現金",
  "クレジットカード",
  "PayPay",
  "楽天ペイ",
  "交通系IC",
  "iD",
  "QUICPay"
].each do |name|
  PaymentMethod.find_or_create_by!(name:)
end
