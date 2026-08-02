class CreateReviews < ActiveRecord::Migration[8.1]
  def change
    create_table :reviews do |t|
      t.references :restaurant, null: false, foreign_key: true
      t.text :body, null: false
      t.integer :rating
      t.date :visited_on

      t.timestamps
    end
  end
end
