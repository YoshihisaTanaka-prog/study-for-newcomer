class Restaurant < ApplicationRecord
  belongs_to :office
  has_many :restaurant_payment_methods, dependent: :destroy
  has_many :payment_methods, through: :restaurant_payment_methods
  has_many :reviews, dependent: :destroy

  validates :name, presence: true
  validates :tabelog_url, presence: true
  validates :price_min, :price_max, numericality: { greater_than_or_equal_to: 0 }, allow_blank: true
  validate :price_range_is_valid

  scope :newest_first, -> { order(created_at: :desc) }

  def price_label
    return "未設定" if price_min.blank? && price_max.blank?
    return "#{price_min}円〜" if price_max.blank?
    return "〜#{price_max}円" if price_min.blank?

    "#{price_min}円〜#{price_max}円"
  end

  private

  def price_range_is_valid
    return if price_min.blank? || price_max.blank?
    return if price_min <= price_max

    errors.add(:price_max, "は最低価格以上にしてください")
  end
end
