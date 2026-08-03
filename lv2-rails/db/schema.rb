# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_08_02_030400) do
  create_table "offices", force: :cascade do |t|
    t.string "address"
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_offices_on_name", unique: true
  end

  create_table "payment_methods", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_payment_methods_on_name", unique: true
  end

  create_table "restaurant_payment_methods", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.integer "payment_method_id", null: false
    t.integer "restaurant_id", null: false
    t.datetime "updated_at", null: false
    t.index ["payment_method_id"], name: "index_restaurant_payment_methods_on_payment_method_id"
    t.index ["restaurant_id", "payment_method_id"], name: "idx_on_restaurant_id_payment_method_id_27d164c0b5", unique: true
    t.index ["restaurant_id"], name: "index_restaurant_payment_methods_on_restaurant_id"
  end

  create_table "restaurants", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "genre"
    t.text "memo"
    t.string "name", null: false
    t.integer "office_id", null: false
    t.integer "price_max"
    t.integer "price_min"
    t.string "tabelog_url", null: false
    t.datetime "updated_at", null: false
    t.index ["genre"], name: "index_restaurants_on_genre"
    t.index ["name"], name: "index_restaurants_on_name"
    t.index ["office_id"], name: "index_restaurants_on_office_id"
  end

  create_table "reviews", force: :cascade do |t|
    t.text "body", null: false
    t.datetime "created_at", null: false
    t.integer "rating"
    t.integer "restaurant_id", null: false
    t.datetime "updated_at", null: false
    t.date "visited_on"
    t.index ["restaurant_id"], name: "index_reviews_on_restaurant_id"
  end

  add_foreign_key "restaurant_payment_methods", "payment_methods"
  add_foreign_key "restaurant_payment_methods", "restaurants"
  add_foreign_key "restaurants", "offices"
  add_foreign_key "reviews", "restaurants"
end
