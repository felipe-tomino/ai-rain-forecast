# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20181101034412) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "gauges", force: :cascade do |t|
    t.string "cod"
    t.string "city"
    t.string "state"
    t.string "name"
    t.string "latitude"
    t.string "longitude"
  end

  create_table "gauges_measures", force: :cascade do |t|
    t.integer  "gauge_id"
    t.datetime "measured_at"
    t.float    "measure"
  end

  add_index "gauges_measures", ["gauge_id"], name: "index_gauges_measures_on_gauge_id", using: :btree

  create_table "tweets", force: :cascade do |t|
    t.integer  "gauge_id"
    t.string   "id_str"
    t.datetime "posted_at"
    t.string   "latitude"
    t.string   "longitude"
    t.boolean  "rain_related"
  end

  add_index "tweets", ["gauge_id"], name: "index_tweets_on_gauge_id", using: :btree

end
