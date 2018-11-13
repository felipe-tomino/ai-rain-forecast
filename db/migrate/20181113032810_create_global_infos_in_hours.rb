class CreateGlobalInfosInHours < ActiveRecord::Migration
  def change
    create_table :global_infos_in_hours do |t|
      t.datetime :time
      t.integer :all_tweets
      t.integer :related_tweets
      t.float :gauge_measures
    end
    create_table :global_infos_in_half_hours do |t|
      t.datetime :time
      t.integer :all_tweets
      t.integer :related_tweets
      t.float :gauge_measures
    end
  end
end
