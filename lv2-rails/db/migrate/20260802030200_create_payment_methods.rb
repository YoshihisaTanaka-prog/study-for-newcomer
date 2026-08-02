class CreatePaymentMethods < ActiveRecord::Migration[8.1]
  def change
    create_table :payment_methods do |t|
      t.string :name, null: false

      t.timestamps
    end

    add_index :payment_methods, :name, unique: true
  end
end
