class CreateOffices < ActiveRecord::Migration[8.1]
  def change
    create_table :offices do |t|
      t.string :name, null: false
      t.string :address

      t.timestamps
    end

    add_index :offices, :name, unique: true
  end
end
