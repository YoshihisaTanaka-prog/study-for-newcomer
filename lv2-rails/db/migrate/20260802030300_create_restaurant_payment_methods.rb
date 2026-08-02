class CreateRestaurantPaymentMethods < ActiveRecord::Migration[8.1]
  def change
    create_table :restaurant_payment_methods do |t|
      t.references :restaurant, null: false, foreign_key: true
      t.references :payment_method, null: false, foreign_key: true

      t.timestamps
    end

    add_index :restaurant_payment_methods,
              [:restaurant_id, :payment_method_id],
              unique: true
  end
end
