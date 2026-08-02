class CreateRestaurants < ActiveRecord::Migration[8.1]
  def change
    create_table :restaurants do |t|
      t.references :office, null: false, foreign_key: true
      t.string :name, null: false
      t.string :genre
      t.string :tabelog_url, null: false
      t.integer :price_min
      t.integer :price_max
      t.text :memo

      t.timestamps
    end

    add_index :restaurants, :name
    add_index :restaurants, :genre
  end
end
