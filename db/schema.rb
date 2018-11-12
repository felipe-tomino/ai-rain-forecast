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

ActiveRecord::Schema.define(version: 20181108213208) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "ar_internal_metadata", primary_key: "key", force: :cascade do |t|
    t.string   "value"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "gauges", id: :bigserial, force: :cascade do |t|
    t.string   "cod"
    t.string   "city"
    t.string   "state"
    t.string   "name"
    t.string   "latitude"
    t.string   "longitude"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "gauges_measures", id: :bigserial, force: :cascade do |t|
    t.integer  "gauge_id",    limit: 8
    t.datetime "measured_at"
    t.float    "measure"
    t.datetime "created_at",            null: false
    t.datetime "updated_at",            null: false
  end

  add_index "gauges_measures", ["gauge_id"], name: "index_gauges_measures_on_gauge_id", using: :btree

  create_table "infos_in_hours", force: :cascade do |t|
    t.integer  "gauge_id"
    t.datetime "hour"
    t.integer  "all_tweets"
    t.integer  "related_tweets"
    t.float    "gauge_measures"
  end

  add_index "infos_in_hours", ["gauge_id"], name: "index_infos_in_hours_on_gauge_id", using: :btree

  create_table "tweets", id: :bigserial, force: :cascade do |t|
    t.integer  "gauge_id",     limit: 8
    t.string   "id_str"
    t.datetime "posted_at"
    t.string   "latitude"
    t.string   "longitude"
    t.string   "rain_related"
    t.datetime "created_at",             null: false
    t.datetime "updated_at",             null: false
  end

  add_index "tweets", ["gauge_id"], name: "index_tweets_on_gauge_id", using: :btree

end
