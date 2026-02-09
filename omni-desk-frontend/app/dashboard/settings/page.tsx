'use client';

import { Save } from 'lucide-react';
import { gradients } from '@/lib/colors';

export default function SettingsPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Settings</h1>
        <p className="text-gray-medium">Configure your OmniDesk AI system</p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white rounded-xl border-2 border-gray-light p-6">
          <h2 className="text-2xl font-bold text-gray-darkest mb-4">General</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">Company Name</label>
              <input
                type="text"
                defaultValue="OmniDesk AI"
                className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">Support Email</label>
              <input
                type="email"
                defaultValue="support@omnidesk.ai"
                className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">Timezone</label>
              <select className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none">
                <option>UTC (GMT+0:00)</option>
                <option>PST (GMT-8:00)</option>
                <option>EST (GMT-5:00)</option>
                <option>IST (GMT+5:30)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Channels */}
        <div className="bg-white rounded-xl border-2 border-gray-light p-6">
          <h2 className="text-2xl font-bold text-gray-darkest mb-4">Channels</h2>
          <div className="space-y-3">
            {[
              { name: 'Email', enabled: true },
              { name: 'WhatsApp', enabled: true },
              { name: 'Web Form', enabled: true },
            ].map((channel) => (
              <label key={channel.name} className="flex items-center gap-3 p-3 rounded-lg hover:bg-purple-50 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked={channel.enabled}
                  className="w-5 h-5 text-primary-purple rounded focus:ring-primary-purple"
                />
                <span className="font-semibold text-gray-darkest">{channel.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* AI Configuration */}
        <div className="bg-white rounded-xl border-2 border-gray-light p-6">
          <h2 className="text-2xl font-bold text-gray-darkest mb-4">AI Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">AI Model</label>
              <select className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none">
                <option>GPT-4 Turbo (Recommended)</option>
                <option>GPT-4</option>
                <option>GPT-3.5 Turbo</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">Response Tone</label>
              <select className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none">
                <option>Professional</option>
                <option>Friendly</option>
                <option>Casual</option>
                <option>Formal</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-darkest font-semibold mb-2">Max Response Length</label>
              <input
                type="number"
                defaultValue="500"
                className="w-full px-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none"
              />
              <p className="text-sm text-gray-medium mt-1">Characters (recommended: 500)</p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <button
          className="flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
          style={{ background: gradients.primary }}
        >
          <Save className="w-5 h-5" />
          Save Changes
        </button>
      </div>
    </div>
  );
}
