<template>
  <div class="publish-view" style="max-width: 1000px; margin: 0 auto; padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <CreationStepper :current-step="4" />
      <button class="btn btn-secondary" @click="goBack" style="margin-left: 20px">
        返回结果页
      </button>
    </div>

    <!-- 标题与副标题 -->
    <div style="margin-bottom: 28px">
      <h1 style="font-size: 26px; font-weight: 700; margin-bottom: 8px">
        发布到小红书
      </h1>
      <p style="color: var(--text-sub); font-size: 15px">
        将生成的内容一键发布至小红书创作者平台，支持多账号安全切换与自主管理
      </p>
    </div>

    <!-- VibeSurf 服务状态检测 -->
    <div class="card" style="margin-bottom: 20px">
      <div style="display: flex; align-items: center; gap: 16px">
        <div style="display: flex; align-items: center; gap: 8px">
          <div
            :style="{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: vibeSurfStatus?.running
                ? 'var(--color-success, #10b981)'
                : 'var(--color-error, #ef4444)',
            }"
          ></div>
          <span style="font-weight: 600">VibeSurf 服务</span>
        </div>
        <span style="color: var(--text-sub); font-size: 14px">
          {{ vibeSurfStatus?.message || "检测中..." }}
        </span>
        <button
          v-if="!vibeSurfStatus?.running"
          class="btn"
          style="margin-left: auto; padding: 8px 16px; font-size: 14px"
          :disabled="vibeSurfActionDisabled"
          @click="handleVibeSurfAction"
        >
          {{ vibeSurfActionLabel }}
        </button>
      </div>
    </div>

    <!-- 小红书登录状态与多账号管理（用户红框区域） -->
    <div
      v-if="vibeSurfStatus?.running"
      class="card account-status-card"
      style="margin-bottom: 24px"
    >
      <div class="account-card-layout">
        <!-- 账号基本信息区 -->
        <div class="account-primary-info">
          <div
            class="status-dot"
            :style="{
              background: (loginStatus?.logged_in && (activeAccount?.creator_authorized ?? loginStatus?.creator_authorized))
                ? 'var(--color-success, #10b981)'
                : (loginStatus?.logged_in ? 'var(--color-warning, #f59e0b)' : 'var(--text-sub, #71717a)'),
            }"
          ></div>

          <!-- 已登录展示账号卡片 -->
          <div v-if="loginStatus?.logged_in" class="logged-in-profile">
            <n-avatar
              round
              :size="38"
              :src="activeAccount?.avatar || undefined"
              fallback-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2371717a'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E"
              class="profile-avatar"
            />
            <div class="profile-meta">
              <div class="profile-name-line">
                <span class="profile-name">{{ activeAccount?.username || loginStatus?.username || "小红书用户" }}</span>
                <span v-if="activeAccount?.alias" class="account-alias-badge">
                  {{ activeAccount.alias }}
                </span>
                <span
                  v-if="activeAccount?.creator_authorized ?? loginStatus?.creator_authorized"
                  class="creator-badge creator-ready"
                >
                  创作者中心已就绪
                </span>
                <span v-else class="creator-badge creator-needed">
                  创作者中心未授权
                </span>
              </div>
              <div class="profile-id-line">
                <span v-if="activeAccount?.red_num">小红书号：{{ activeAccount.red_num }}</span>
                <span v-else>{{ loginStatus?.message || "登录态就绪" }}</span>
              </div>
            </div>
          </div>

          <!-- 未登录提示 -->
          <div v-else class="logged-out-profile">
            <span style="font-weight: 600; margin-right: 8px;">小红书登录状态</span>
            <span style="color: var(--text-sub); font-size: 14px;">
              {{ loginStatus?.message || "未登录，请添加或登录小红书账号" }}
            </span>
          </div>
        </div>

        <!-- 动作操作组 -->
        <div class="account-actions-area">
          <!-- 账号切换下拉 -->
          <n-popover
            v-if="accounts.length > 0"
            trigger="click"
            placement="bottom-end"
            v-model:show="showSwitcherPopover"
          >
            <template #trigger>
              <button
                class="btn btn-secondary account-switch-trigger"
                :disabled="switchingAccount"
                title="选择发布账号"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px;">
                  <path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/>
                </svg>
                <span>{{ switchingAccount ? "切换中..." : "切换账号" }}</span>
                <span v-if="accounts.length > 1" class="account-count-badge">{{ accounts.length }}</span>
              </button>
            </template>
            <div class="account-switcher-popover">
              <div class="popover-header">
                <div style="font-weight: 600; font-size: 13px; color: var(--text-main);">选择发布账号</div>
                <div style="font-size: 11px; color: var(--text-sub); margin-top: 2px;">
                  点击直接切换，各账号登录态独立保存
                </div>
              </div>
              <div class="popover-list">
                <div
                  v-for="acc in accounts"
                  :key="acc.id"
                  class="popover-item"
                  :class="{ 'item-active': acc.id === activeAccount?.id }"
                  @click="handleSelectAccount(acc.id)"
                >
                  <n-avatar
                    round
                    :size="30"
                    :src="acc.avatar || undefined"
                    fallback-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2371717a'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E"
                  />
                  <div class="popover-item-info">
                    <div class="popover-item-name">
                      {{ acc.username }}
                      <span v-if="acc.alias" class="account-alias-badge">{{ acc.alias }}</span>
                    </div>
                    <div class="popover-item-sub">
                      {{ acc.red_num ? `小红书号: ${acc.red_num}` : (acc.creator_authorized ? '创作者已就绪' : '需授权') }}
                    </div>
                  </div>
                  <span v-if="acc.id === activeAccount?.id" class="popover-active-check">✓</span>
                </div>
              </div>
              <div class="popover-footer">
                <button class="popover-footer-btn" @click="openAddAccountModal">
                  + 添加新账号
                </button>
                <button class="popover-footer-btn" @click="openManageModal">
                  管理全部账号 ({{ accounts.length }})
                </button>
              </div>
            </div>
          </n-popover>

          <!-- 添加账号按钮 -->
          <button
            class="btn"
            style="padding: 8px 14px; font-size: 14px"
            @click="openAddAccountModal"
          >
            <span style="font-weight: 600; margin-right: 4px;">+</span> 添加账号
          </button>

          <!-- 管理账号按钮 -->
          <button
            v-if="accounts.length > 0"
            class="btn btn-ghost"
            style="padding: 8px 12px; font-size: 14px"
            @click="showAccountManageModal = true"
            title="管理多账号"
          >
            管理
          </button>

          <!-- 授权创作者中心按钮（仅在主站已登录但创作者中心未授权时出现） -->
          <button
            v-if="loginStatus?.logged_in && !loginStatus?.creator_authorized"
            class="btn btn-primary"
            style="padding: 8px 16px; font-size: 14px"
            @click="openCreator"
            :disabled="openingCreator"
          >
            {{ openingCreator ? "打开中..." : "授权创作者中心" }}
          </button>

          <!-- 初始无账号时扫码登录 -->
          <button
            v-if="!loginStatus?.logged_in && accounts.length === 0"
            class="btn btn-primary"
            style="padding: 8px 16px; font-size: 14px"
            @click="openAddAccountModal"
          >
            扫码登录主站
          </button>

          <!-- 刷新状态按钮 -->
          <button
            class="btn"
            style="padding: 8px 14px; font-size: 14px"
            :disabled="checkingLogin"
            @click="handleRefreshAll"
          >
            {{ checkingLogin ? "刷新中..." : "刷新状态" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 内容预览与发布操作 -->
    <div
      v-if="vibeSurfStatus?.running && store.images.length > 0"
      class="card"
    >
      <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 20px">
        发布预览
      </h2>

      <!-- 发布目标账号横幅提示（清晰指明发布到哪个账号） -->
      <div class="publish-target-banner">
        <div class="target-left">
          <span style="font-size: 16px;">🎯</span>
          <span style="font-weight: 600; font-size: 14px; color: var(--text-main);">当前将发布至：</span>
          <n-avatar
            round
            :size="26"
            :src="activeAccount?.avatar || undefined"
            fallback-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2371717a'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E"
          />
          <span class="target-account-name">
            {{ activeAccount?.username || loginStatus?.username || "当前活跃账号" }}
          </span>
          <span v-if="activeAccount?.alias" class="account-alias-badge">
            {{ activeAccount.alias }}
          </span>
          <span v-if="activeAccount?.red_num" class="target-account-id">
            (号: {{ activeAccount.red_num }})
          </span>
          <span
            v-if="activeAccount?.creator_authorized ?? loginStatus?.creator_authorized"
            class="creator-badge creator-ready"
          >
            创作者就绪
          </span>
          <span v-else class="creator-badge creator-needed">
            需创作者授权
          </span>
        </div>

        <div v-if="accounts.length > 1" class="target-right">
          <n-popover trigger="click" placement="bottom-end">
            <template #trigger>
              <button class="target-switch-btn">
                切换目标账号 ▾
              </button>
            </template>
            <div class="account-switcher-popover">
              <div class="popover-header">
                <div style="font-weight: 600; font-size: 13px;">选择本次发布的小红书账号</div>
              </div>
              <div class="popover-list">
                <div
                  v-for="acc in accounts"
                  :key="acc.id"
                  class="popover-item"
                  :class="{ 'item-active': acc.id === activeAccount?.id }"
                  @click="handleSelectAccount(acc.id)"
                >
                  <n-avatar round :size="28" :src="acc.avatar || undefined" />
                  <div class="popover-item-info">
                    <div class="popover-item-name">
                      {{ acc.username }}
                      <span v-if="acc.alias" class="account-alias-badge">{{ acc.alias }}</span>
                    </div>
                    <div class="popover-item-sub">
                      {{ acc.red_num ? `小红书号: ${acc.red_num}` : (acc.creator_authorized ? '就绪' : '需授权') }}
                    </div>
                  </div>
                  <span v-if="acc.id === activeAccount?.id" class="popover-active-check">✓</span>
                </div>
              </div>
            </div>
          </n-popover>
        </div>
      </div>

      <!-- 图片预览 -->
      <div style="margin-bottom: 24px">
        <h3
          style="font-size: 14px; color: var(--text-sub); margin-bottom: 12px"
        >
          图片 ({{ store.images.length }} 张)
        </h3>
        <n-image-group>
          <div
            style="
              display: flex;
              gap: 12px;
              overflow-x: auto;
              padding-bottom: 12px;
            "
          >
            <div
              v-for="image in store.images"
              :key="image.index"
              class="preview-image-wrapper"
            >
              <n-image
                :src="image.url"
                :alt="`第 ${image.index + 1} 页`"
                object-fit="cover"
              />
            </div>
          </div>
        </n-image-group>
      </div>

      <!-- 标题 -->
      <div style="margin-bottom: 20px">
        <h3 style="font-size: 14px; color: var(--text-sub); margin-bottom: 8px">
          标题
        </h3>
        <n-select
          v-model:value="selectedTitle"
          :options="titleOptions"
          size="large"
          placeholder="请选择标题"
        />
      </div>

      <!-- 正文 -->
      <div style="margin-bottom: 20px">
        <h3 style="font-size: 14px; color: var(--text-sub); margin-bottom: 8px">
          正文
        </h3>
        <n-input
          v-model:value="copywriting"
          type="textarea"
          :autosize="{
            minRows: 10,
            maxRows: 20,
          }"
          placeholder="请输入正文"
          size="large"
          maxlength="1000"
          show-count
        />
      </div>

      <!-- 标签 -->
      <div style="margin-bottom: 24px">
        <h3 style="font-size: 14px; color: var(--text-sub); margin-bottom: 8px">
          标签
        </h3>
        <div style="display: flex; flex-wrap: wrap; gap: 8px">
          <span
            v-for="(tag, idx) in store.content.tags"
            :key="idx"
            class="xhs-tag"
          >
            #{{ tag }}
          </span>
        </div>
      </div>

      <!-- 发布按钮 -->
      <div style="display: flex; gap: 12px">
        <button
          class="btn btn-primary"
          style="flex: 1; padding: 14px; font-size: 16px"
          :disabled="!canPublish || isPublishing"
          @click="startPublish"
        >
          {{ isPublishing ? "发布中..." : "确认发布" }}
        </button>
      </div>

      <!-- 发布进度 -->
      <div
        v-if="isPublishing && publishProgress.length > 0"
        style="
          margin-top: 24px;
          border-top: 1px solid var(--border-color);
          padding-top: 20px;
        "
      >
        <h3
          style="font-size: 14px; color: var(--text-sub); margin-bottom: 12px"
        >
          发布进度
        </h3>
        <div style="display: flex; flex-direction: column; gap: 8px">
          <div
            v-for="(step, idx) in publishProgress"
            :key="idx"
            style="
              display: flex;
              align-items: center;
              gap: 12px;
              padding: 12px;
              background: var(--bg-secondary);
              border-radius: 8px;
            "
          >
            <div
              :style="{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                background:
                  step.success === true
                    ? 'var(--color-success)'
                    : step.success === false
                      ? 'var(--color-error)'
                      : 'var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-main)',
                fontSize: '12px',
              }"
            >
              <span v-if="step.success === true">✓</span>
              <span v-else-if="step.success === false">✗</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div style="flex: 1">
              <div style="font-weight: 500">{{ step.step }}</div>
              <div style="font-size: 13px; color: var(--text-sub)">
                {{ step.message }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 发布结果 -->
      <div
        v-if="publishResult"
        style="
          margin-top: 24px;
          border-top: 1px solid var(--border-color);
          padding-top: 20px;
        "
      >
        <div
          :style="{
            padding: '16px',
            borderRadius: '8px',
            background: publishResult.success
              ? 'var(--color-success-bg, rgba(16, 185, 129, 0.1))'
              : 'var(--color-error-bg, rgba(239, 68, 68, 0.1))',
            border: `1px solid ${publishResult.success ? 'var(--color-success-border, rgba(16, 185, 129, 0.2))' : 'var(--color-error-border, rgba(239, 68, 68, 0.2))'}`,
          }"
        >
          <div style="font-weight: 600; margin-bottom: 8px">
            {{ publishResult.success ? "发布成功!" : "发布失败" }}
          </div>
          <div
            v-if="publishResult.post_url"
            style="font-size: 14px"
          >
            <div style="margin-bottom: 6px">文章链接：</div>
            <a
              :href="publishResult.post_url"
              target="_blank"
              rel="noopener noreferrer"
              style="
                color: var(--primary);
                word-break: break-all;
                line-height: 1.5;
              "
            >
              {{ publishResult.post_url }}
            </a>
            <button
              class="btn"
              style="margin-top: 10px; padding: 6px 12px; font-size: 13px"
              @click="copyPostUrl"
            >
              复制链接
            </button>
          </div>
          <div
            v-if="publishResult.error"
            style="font-size: 14px; color: var(--color-error)"
          >
            {{ publishResult.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- 无内容提示 -->
    <div
      v-else-if="store.images.length === 0"
      class="card"
    >
      <div
        style="text-align: center; padding: 48px 24px; color: var(--text-sub)"
      >
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          style="margin: 0 auto 16px"
        >
          <rect
            x="3"
            y="3"
            width="18"
            height="18"
            rx="2"
            ry="2"
          ></rect>
          <circle
            cx="8.5"
            cy="8.5"
            r="1.5"
          ></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <p style="font-size: 16px; margin-bottom: 16px">还没有生成内容</p>
        <button
          class="btn btn-primary"
          @click="goHome"
        >
          去生成
        </button>
      </div>
    </div>

    <!-- 弹窗 1：添加小红书账号弹窗 -->
    <n-modal v-model:show="showAddAccountModal" :mask-closable="false">
      <n-card
        style="width: 440px; border-radius: 16px; background: var(--bg-card, #16161a);"
        title="添加小红书账号"
        :bordered="false"
        size="large"
        role="dialog"
        aria-modal="true"
        closable
        @close="handleCloseAddModal"
      >
        <p style="color: var(--text-sub); font-size: 13px; margin-bottom: 16px; line-height: 1.5;">
          登录新的小红书账号，系统将隔离存储各账号登录凭证，不会覆盖或删除现有账号。
        </p>

        <n-tabs v-model:value="addAccountTab" type="segment" animated>
          <!-- 选项卡 1：扫码添加 -->
          <n-tab-pane name="qrcode" tab="扫码登录添加">
            <div style="padding-top: 14px; text-align: center;">
              <p style="color: var(--text-sub); font-size: 12px; margin-bottom: 14px;">
                {{ addAccountMessage || "请使用手机小红书 App 扫描下方二维码登录" }}
              </p>

              <div style="display: flex; justify-content: center; align-items: center; min-height: 220px; margin-bottom: 16px;">
                <n-spin v-if="startingAddAccount" size="large" />
                <img
                  v-else-if="addAccountQrcode"
                  :src="addAccountQrcode"
                  alt="小红书登录二维码"
                  style="width: 210px; height: 210px; border-radius: 8px; border: 1px solid var(--border-color, #27272a)"
                />
                <div v-else style="color: var(--color-error); font-size: 13px;">
                  获取二维码失败，请检查服务状态
                </div>
              </div>

              <div style="display: flex; gap: 10px; justify-content: center;">
                <button
                  class="btn btn-primary"
                  style="padding: 8px 18px; font-size: 14px;"
                  @click="handleManualDoneQr"
                >
                  我已完成扫码
                </button>
                <button
                  class="btn"
                  style="padding: 8px 16px; font-size: 14px;"
                  @click="startQrAddFlow"
                  :disabled="startingAddAccount"
                >
                  刷新二维码
                </button>
                <button
                  class="btn btn-ghost"
                  style="padding: 8px 16px; font-size: 14px;"
                  @click="handleCloseAddModal"
                >
                  取消
                </button>
              </div>
            </div>
          </n-tab-pane>

          <!-- 选项卡 2：Cookie 导入 -->
          <n-tab-pane name="cookie" tab="Cookie 快速导入">
            <div style="padding-top: 14px;">
              <p style="color: var(--text-sub); font-size: 12px; margin-bottom: 12px; line-height: 1.5;">
                支持直接粘贴浏览器 Cookie（JSON 列表或 web_session 键值对字符串），系统将自动校验其创作者权限并绑定。
              </p>

              <div style="margin-bottom: 14px;">
                <div style="font-size: 13px; margin-bottom: 6px; font-weight: 500;">
                  Cookie 内容 <span style="color: var(--color-error);">*</span>
                </div>
                <n-input
                  v-model:value="importCookieText"
                  type="textarea"
                  :autosize="{ minRows: 4, maxRows: 8 }"
                  placeholder="粘贴 JSON 格式 Cookie 或 web_session=...; a1=... 字符串"
                  size="small"
                />
              </div>

              <div style="margin-bottom: 18px;">
                <div style="font-size: 13px; margin-bottom: 6px; font-weight: 500;">
                  账号备注别名（选填）
                </div>
                <n-input
                  v-model:value="importCookieAlias"
                  placeholder="例如：好物分享号、数码备用号"
                  maxlength="20"
                  size="small"
                />
              </div>

              <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn" @click="handleCloseAddModal">取消</button>
                <button
                  class="btn btn-primary"
                  :disabled="importingCookie || !importCookieText.trim()"
                  @click="handleImportCookie"
                >
                  {{ importingCookie ? "验证并导入中..." : "验证并导入" }}
                </button>
              </div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </n-card>
    </n-modal>

    <!-- 弹窗 2：小红书多账号管理弹窗 -->
    <n-modal v-model:show="showAccountManageModal">
      <n-card
        style="width: 640px; border-radius: 16px; background: var(--bg-card, #16161a);"
        title="小红书多账号管理"
        :bordered="false"
        size="large"
        role="dialog"
        aria-modal="true"
        closable
        @close="showAccountManageModal = false"
      >
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
          <span style="color: var(--text-sub); font-size: 13px;">
            已绑定 {{ accounts.length }} 个账号，随时选择发布目标，凭据互不干扰。
          </span>
          <button class="btn btn-primary" style="padding: 6px 14px; font-size: 13px;" @click="openAddFromManage">
            + 添加新账号
          </button>
        </div>

        <!-- 账号列表 -->
        <div class="manage-account-list">
          <div
            v-for="acc in accounts"
            :key="acc.id"
            class="manage-account-item"
            :class="{ 'item-active': acc.id === activeAccount?.id }"
          >
            <n-avatar
              round
              :size="42"
              :src="acc.avatar || undefined"
              fallback-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2371717a'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E"
            />
            <div class="manage-account-info">
              <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span class="manage-account-name">{{ acc.username }}</span>
                <span v-if="acc.alias" class="account-alias-badge">{{ acc.alias }}</span>
                <span v-if="acc.id === activeAccount?.id" class="active-badge">当前发布账号</span>
              </div>
              <div style="font-size: 12px; color: var(--text-sub); margin-top: 5px;">
                <span v-if="acc.red_num">小红书号: {{ acc.red_num }}</span>
                <span v-if="acc.red_num" style="margin: 0 6px;">·</span>
                <span :style="{ color: acc.creator_authorized ? 'var(--color-success, #10b981)' : 'var(--color-warning, #f59e0b)' }">
                  {{ acc.creator_authorized ? '创作者中心已授权' : '创作者中心未授权' }}
                </span>
              </div>
            </div>

            <div class="manage-account-actions">
              <button
                v-if="acc.id !== activeAccount?.id"
                class="btn btn-secondary"
                style="padding: 4px 12px; font-size: 12px;"
                :disabled="switchingAccount"
                @click="handleSelectAccount(acc.id)"
              >
                设为发布账号
              </button>
              <button
                class="btn btn-ghost"
                style="padding: 4px 8px; font-size: 12px;"
                @click="openAliasModal(acc)"
                title="修改别名备注"
              >
                备注
              </button>
              <button
                class="btn btn-ghost"
                style="padding: 4px 8px; font-size: 12px;"
                @click="handleRefreshSingleAccount(acc.id)"
                title="刷新此账号信息"
              >
                刷新
              </button>
              <n-popconfirm @positive-click="handleDeleteAccount(acc.id)">
                <template #trigger>
                  <button
                    class="btn btn-ghost"
                    style="padding: 4px 8px; font-size: 12px; color: var(--color-error, #ef4444);"
                    title="删除账号"
                  >
                    删除
                  </button>
                </template>
                确定要删除账号“{{ acc.username }}”的登录凭据吗？删除后不可撤销。
              </n-popconfirm>
            </div>
          </div>
        </div>
      </n-card>
    </n-modal>

    <!-- 弹窗 3：修改账号备注弹窗 -->
    <n-modal v-model:show="showAliasModal">
      <n-card
        style="width: 380px; border-radius: 14px; background: var(--bg-card, #16161a);"
        title="修改账号备注"
        :bordered="false"
        size="medium"
      >
        <p style="font-size: 13px; color: var(--text-sub); margin-bottom: 12px;">
          设置易于识别的备注别名（例如：日常穿搭、科技数码）：
        </p>
        <n-input
          v-model:value="newAliasValue"
          placeholder="输入账号备注"
          maxlength="20"
          show-count
          clearable
          style="margin-bottom: 16px;"
        />
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <button class="btn" @click="showAliasModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSaveAlias">保存备注</button>
        </div>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useGeneratorStore } from "../stores/generator";
import {
  checkVibeSurfStatus,
  startVibeSurfService,
  installXiaohongshuMcp,
  checkXiaohongshuLogin,
  openCreatorLogin,
  publishToXiaohongshu,
  fetchXiaohongshuAccounts,
  switchXiaohongshuAccount,
  startAddXiaohongshuAccount,
  checkAddXiaohongshuAccountStatus,
  cancelAddXiaohongshuAccount,
  importXiaohongshuCookies,
  updateXiaohongshuAccountAlias,
  deleteXiaohongshuAccount,
  refreshXiaohongshuAccountStatus,
  type VibeSurfStatus,
  type LoginStatus,
  type PublishProgressEvent,
  type XiaohongshuAccount,
} from "../api";
import {
  useMessage,
  NImage,
  NImageGroup,
  NSelect,
  NInput,
  NModal,
  NCard,
  NAvatar,
  NPopover,
  NPopconfirm,
  NTabs,
  NTabPane,
  NSpin,
} from "naive-ui";
import CreationStepper from "../components/home/CreationStepper.vue";

const router = useRouter();
const store = useGeneratorStore();
const message = useMessage();

// VibeSurf 与通用登录状态
const vibeSurfStatus = ref<VibeSurfStatus | null>(null);
const loginStatus = ref<LoginStatus | null>(null);
const openingCreator = ref(false);
const checkingLogin = ref(false);
const startingVibeSurf = ref(false);
const installingMcp = ref(false);

// 多账号管理状态
const accounts = ref<XiaohongshuAccount[]>([]);
const activeAccountId = ref<string | null>(null);
const switchingAccount = ref(false);
const showSwitcherPopover = ref(false);
const showAddAccountModal = ref(false);
const showAccountManageModal = ref(false);
const showAliasModal = ref(false);

// 添加账号弹窗内部状态
const addAccountTab = ref<"qrcode" | "cookie">("qrcode");
const startingAddAccount = ref(false);
const addAccountQrcode = ref("");
const addAccountMessage = ref("");
const addAccountPolling = ref<number | null>(null);
const importCookieText = ref("");
const importCookieAlias = ref("");
const importingCookie = ref(false);

// 修改别名内部状态
const editingAliasAccount = ref<XiaohongshuAccount | null>(null);
const newAliasValue = ref("");

// 发布相关状态
const isPublishing = ref(false);
const publishProgress = ref<PublishProgressEvent[]>([]);
const publishResult = ref<{
  success: boolean;
  post_url?: string;
  error?: string;
} | null>(null);

// 表单数据
const selectedTitle = ref("");
const copywriting = ref("");

// 计算当前活跃账号
const activeAccount = computed<XiaohongshuAccount | null>(() => {
  if (!accounts.value.length) return null;
  const found = accounts.value.find((a) => a.id === activeAccountId.value);
  return found || accounts.value[0] || null;
});

// 计算选项
const titleOptions = computed(() => {
  return store.content.titles.map((title) => ({
    label: title,
    value: title,
  }));
});

// 计算是否可发布
const canPublish = computed(() => {
  const hasAccountReady = Boolean(
    activeAccount.value?.creator_authorized ?? loginStatus.value?.creator_authorized
  );
  return (
    vibeSurfStatus.value?.running &&
    loginStatus.value?.logged_in &&
    hasAccountReady &&
    store.images.length > 0 &&
    selectedTitle.value &&
    copywriting.value
  );
});

const canStartService = computed(() => {
  const status = vibeSurfStatus.value;
  return Boolean(
    status && !status.running && status.binary_installed !== false,
  );
});

const needInstallMcp = computed(() => {
  const status = vibeSurfStatus.value;
  return Boolean(
    status && !status.running && status.binary_installed === false,
  );
});

const vibeSurfActionLabel = computed(() => {
  if (needInstallMcp.value) {
    return installingMcp.value ? "安装中..." : "安装并检测";
  }
  if (canStartService.value) {
    return startingVibeSurf.value ? "启动中..." : "启动服务";
  }
  return "重新检测";
});

const vibeSurfActionDisabled = computed(
  () => startingVibeSurf.value || installingMcp.value,
);

// ---------------- 基础导航方法 ----------------

const goBack = () => {
  router.push("/redbook/result");
};

const goHome = () => {
  router.push("/");
};

// ---------------- VibeSurf 服务控制 ----------------

const checkVibeSurf = async () => {
  try {
    const result = await checkVibeSurfStatus();
    if (result.success && result.status) {
      vibeSurfStatus.value = result.status;
    } else {
      vibeSurfStatus.value = {
        running: false,
        message: result.error || "检测失败",
      };
    }
  } catch (e: any) {
    vibeSurfStatus.value = { running: false, message: e.message };
  }
};

const startVibeSurf = async () => {
  if (startingVibeSurf.value) return;
  startingVibeSurf.value = true;
  try {
    vibeSurfStatus.value = {
      running: false,
      message: "正在启动服务...",
    };
    const res = await startVibeSurfService();
    if (res.success || res.running) {
      message.success("VibeSurf 服务已启动");
    } else {
      message.error("启动服务失败: " + (res.error || "未知错误"));
    }
    await checkVibeSurf();
    if (vibeSurfStatus.value?.running) {
      await loadAccounts();
      await checkLogin(false);
    }
  } catch (e: any) {
    vibeSurfStatus.value = { running: false, message: e.message || "启动失败" };
    message.error("启动服务失败: " + (e?.message || "未知错误"));
  } finally {
    startingVibeSurf.value = false;
  }
};

const installMcp = async () => {
  if (installingMcp.value) return;
  installingMcp.value = true;
  try {
    vibeSurfStatus.value = {
      running: false,
      binary_installed: false,
      message: "正在安装 xiaohongshu-mcp...",
    };

    const result = await installXiaohongshuMcp();
    if (!result.success) {
      message.error("安装失败: " + (result.error || "未知错误"));
      await checkVibeSurf();
      return;
    }

    message.success(result.message || "安装完成");
    await checkVibeSurf();
    if (canStartService.value) {
      await startVibeSurf();
    }
  } catch (e: any) {
    message.error("安装失败: " + (e?.message || "未知错误"));
    await checkVibeSurf();
  } finally {
    installingMcp.value = false;
  }
};

const handleVibeSurfAction = async () => {
  if (needInstallMcp.value) {
    await installMcp();
    return;
  }
  if (canStartService.value) {
    await startVibeSurf();
    return;
  }
  await checkVibeSurf();
};

// ---------------- 登录状态检测 ----------------

const checkLogin = async (force: boolean = false) => {
  if (checkingLogin.value) return;
  checkingLogin.value = true;
  try {
    const result = await checkXiaohongshuLogin();
    if (result.success && result.status) {
      loginStatus.value = result.status;
      if (result.status.active_account) {
        activeAccountId.value = result.status.active_account.id;
      }
    } else {
      loginStatus.value = {
        logged_in: false,
        creator_authorized: false,
        message: result.error || "检测失败",
      };
    }
  } catch (e: any) {
    loginStatus.value = { logged_in: false, creator_authorized: false, message: e.message };
  } finally {
    checkingLogin.value = false;
  }
};

const openCreator = async () => {
  openingCreator.value = true;
  try {
    const result = await openCreatorLogin();
    if (!result.success) {
      message.error("打开创作者中心登录失败: " + (result.error || "未知错误"));
    } else {
      message.info(result.message || "请在创作者平台完成登录，登录后点击【刷新状态】");
    }
  } catch (e: any) {
    message.error("打开创作者中心失败: " + e.message);
  } finally {
    openingCreator.value = false;
  }
};

// ---------------- 多账号操作 ----------------

const loadAccounts = async () => {
  try {
    const res = await fetchXiaohongshuAccounts();
    if (res.success && Array.isArray(res.accounts)) {
      accounts.value = res.accounts;
      if (res.active_account_id) {
        activeAccountId.value = res.active_account_id;
      } else if (res.accounts.length > 0) {
        activeAccountId.value = res.accounts[0].id;
      }
    }
  } catch (e: any) {
    console.error("加载账号列表失败:", e);
  }
};

const handleSelectAccount = async (accId: string) => {
  if (accId === activeAccountId.value) {
    showSwitcherPopover.value = false;
    return;
  }
  switchingAccount.value = true;
  showSwitcherPopover.value = false;
  try {
    const res = await switchXiaohongshuAccount(accId);
    if (res.success) {
      message.success(res.message || "账号切换成功！");
      await loadAccounts();
      await checkLogin(false);
    } else {
      message.error(res.error || "切换账号失败");
    }
  } catch (e: any) {
    message.error("切换账号异常: " + (e?.message || "未知错误"));
  } finally {
    switchingAccount.value = false;
  }
};

const openAddAccountModal = async () => {
  showSwitcherPopover.value = false;
  showAddAccountModal.value = true;
  addAccountTab.value = "qrcode";
  await startQrAddFlow();
};

const openAddFromManage = async () => {
  showAccountManageModal.value = false;
  await openAddAccountModal();
};

const openManageModal = () => {
  showSwitcherPopover.value = false;
  showAccountManageModal.value = true;
};

// 扫码流程
const startQrAddFlow = async () => {
  startingAddAccount.value = true;
  addAccountQrcode.value = "";
  addAccountMessage.value = "正在获取小红书登录二维码...";
  stopAddAccountPolling();

  try {
    const res = await startAddXiaohongshuAccount();
    if (res.success && res.qrcode) {
      addAccountQrcode.value = res.qrcode;
      addAccountMessage.value = res.message || "请使用手机小红书 App 扫描二维码添加账号";
      startAddAccountPolling();
    } else {
      addAccountMessage.value = res.error || "获取二维码失败";
      message.error(res.error || "获取二维码失败，请确保服务已启动并重试");
    }
  } catch (e: any) {
    addAccountMessage.value = e?.message || "获取二维码异常";
    message.error("获取二维码失败: " + (e?.message || "未知错误"));
  } finally {
    startingAddAccount.value = false;
  }
};

const startAddAccountPolling = () => {
  stopAddAccountPolling();
  addAccountPolling.value = window.setInterval(async () => {
    try {
      const res = await checkAddXiaohongshuAccountStatus();
      if (res.success && res.logged_in) {
        stopAddAccountPolling();
        message.success(res.message || "小红书账号添加成功！");
        showAddAccountModal.value = false;
        await loadAccounts();
        await checkLogin(false);
      }
    } catch {
      // 静默轮询
    }
  }, 2000);
};

const stopAddAccountPolling = () => {
  if (addAccountPolling.value) {
    clearInterval(addAccountPolling.value);
    addAccountPolling.value = null;
  }
};

const handleCloseAddModal = async () => {
  stopAddAccountPolling();
  showAddAccountModal.value = false;
  try {
    await cancelAddXiaohongshuAccount();
    await loadAccounts();
    await checkLogin(false);
  } catch {
    // 静默兜底
  }
};

const handleManualDoneQr = async () => {
  try {
    const res = await checkAddXiaohongshuAccountStatus();
    if (res.success && res.logged_in) {
      stopAddAccountPolling();
      message.success(res.message || "小红书账号添加成功！");
      showAddAccountModal.value = false;
      await loadAccounts();
      await checkLogin(false);
    } else {
      message.warning("尚未检测到扫码成功，请在手机端确认授权登录后重试");
    }
  } catch (e: any) {
    message.error("检测登录状态失败: " + (e?.message || "未知错误"));
  }
};

// Cookie 导入流程
const handleImportCookie = async () => {
  if (!importCookieText.value.trim()) {
    message.warning("请粘贴 Cookie 内容");
    return;
  }
  importingCookie.value = true;
  try {
    const res = await importXiaohongshuCookies(
      importCookieText.value.trim(),
      importCookieAlias.value.trim()
    );
    if (res.success) {
      message.success(res.message || "Cookie 导入成功！已切换至新账号");
      importCookieText.value = "";
      importCookieAlias.value = "";
      showAddAccountModal.value = false;
      await loadAccounts();
      await checkLogin(false);
    } else {
      message.error(res.error || "导入失败，请检查 Cookie 有效性");
    }
  } catch (e: any) {
    message.error("导入失败: " + (e?.message || "未知错误"));
  } finally {
    importingCookie.value = false;
  }
};

// 账号备注修改
const openAliasModal = (acc: XiaohongshuAccount) => {
  editingAliasAccount.value = acc;
  newAliasValue.value = acc.alias || "";
  showAliasModal.value = true;
};

const handleSaveAlias = async () => {
  if (!editingAliasAccount.value) return;
  try {
    const res = await updateXiaohongshuAccountAlias(
      editingAliasAccount.value.id,
      newAliasValue.value.trim()
    );
    if (res.success) {
      message.success("备注别名已保存");
      showAliasModal.value = false;
      await loadAccounts();
    } else {
      message.error(res.error || "保存失败");
    }
  } catch (e: any) {
    message.error("保存失败: " + (e?.message || "未知错误"));
  }
};

// 账号删除
const handleDeleteAccount = async (accId: string) => {
  try {
    const res = await deleteXiaohongshuAccount(accId);
    if (res.success) {
      message.success(res.message || "账号已删除");
      await loadAccounts();
      await checkLogin(false);
    } else {
      message.error(res.error || "删除失败");
    }
  } catch (e: any) {
    message.error("删除账号失败: " + (e?.message || "未知错误"));
  }
};

// 账号状态刷新
const handleRefreshAll = async () => {
  await loadAccounts();
  await checkLogin(true);
  if (activeAccountId.value) {
    await refreshXiaohongshuAccountStatus(activeAccountId.value);
    await loadAccounts();
  }
};

const handleRefreshSingleAccount = async (accId: string) => {
  try {
    const res = await refreshXiaohongshuAccountStatus(accId);
    if (res.success) {
      message.success(res.message || "账号状态已更新");
      await loadAccounts();
    } else {
      message.error(res.error || "刷新失败");
    }
  } catch (e: any) {
    message.error("刷新失败: " + (e?.message || "未知错误"));
  }
};

// ---------------- 发布流程 ----------------

const copyPostUrl = async () => {
  const url = publishResult.value?.post_url;
  if (!url) return;
  try {
    await navigator.clipboard.writeText(url);
    message.success("链接已复制");
  } catch (e: any) {
    message.error("复制失败: " + (e?.message || "未知错误"));
  }
};

const startPublish = async () => {
  if (!canPublish.value) return;

  isPublishing.value = true;
  publishProgress.value = [];
  publishResult.value = null;

  const imageUrls = store.images.map((img) => img.url);

  publishToXiaohongshu(
    {
      images: imageUrls,
      title: selectedTitle.value,
      content: copywriting.value,
      tags: store.content.tags,
    },
    // onProgress
    (event: PublishProgressEvent) => {
      publishProgress.value.push(event);
    },
    // onComplete
    (event: PublishProgressEvent) => {
      isPublishing.value = false;
      publishResult.value = {
        success: event.success || false,
        post_url: event.post_url,
        error: event.error,
      };
      // 发布成功后刷新活跃账号
      loadAccounts();
    },
    // onError
    (event: PublishProgressEvent) => {
      isPublishing.value = false;
      publishResult.value = {
        success: false,
        error: event.error || "发布失败",
      };
    },
    // onStreamError
    (error: Error) => {
      isPublishing.value = false;
      publishResult.value = {
        success: false,
        error: error.message,
      };
    },
  );
};

// ---------------- 生命周期 ----------------

onMounted(async () => {
  if (store.content.titles.length > 0) {
    selectedTitle.value = store.content.titles[0];
  }
  copywriting.value = store.content.copywriting || "";

  // 1. 加载账号列表
  await loadAccounts();

  // 2. 检测 VibeSurf 状态
  await checkVibeSurf();
  if (canStartService.value) {
    await startVibeSurf();
  }

  // 3. 服务就绪时探活登录态
  if (vibeSurfStatus.value?.running) {
    await checkLogin(false);
  }
});

onUnmounted(() => {
  stopAddAccountPolling();
});
</script>

<style scoped>
.card {
  background: var(--bg-card, #16161a);
  border-radius: 14px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color, #27272a);
}

/* 账号卡片核心排版 */
.account-status-card {
  transition: border-color 0.2s ease;
}

.account-card-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.account-primary-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 280px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

.logged-in-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-avatar {
  border: 2px solid rgba(255, 36, 66, 0.4);
  flex-shrink: 0;
}

.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.profile-name-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.profile-name {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-main, #f4f4f5);
}

.profile-id-line {
  font-size: 13px;
  color: var(--text-sub, #a1a1aa);
}

.logged-out-profile {
  display: flex;
  align-items: center;
}

/* 徽章样式 */
.account-alias-badge {
  background: rgba(255, 36, 66, 0.12);
  color: #ff2442;
  border: 1px solid rgba(255, 36, 66, 0.25);
  border-radius: 4px;
  font-size: 11px;
  padding: 1px 6px;
  font-weight: 500;
}

.creator-badge {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 4px;
  font-weight: 500;
}

.creator-badge.creator-ready {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.creator-badge.creator-needed {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

/* 动作操作区 */
.account-actions-area {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.account-switch-trigger {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  font-size: 14px;
  background: var(--bg-secondary, #1c1c21);
  border: 1px solid var(--border-color, #27272a);
  color: var(--text-main, #f4f4f5);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.account-switch-trigger:hover {
  border-color: #ff2442;
  background: rgba(255, 36, 66, 0.06);
}

.account-count-badge {
  margin-left: 6px;
  background: rgba(255, 36, 66, 0.2);
  color: #ff2442;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 600;
}

/* 切换下拉浮层 */
.account-switcher-popover {
  width: 310px;
  padding: 6px;
  background: var(--bg-card, #16161a);
}

.popover-header {
  padding: 6px 10px 10px;
  border-bottom: 1px solid var(--border-color, #27272a);
  margin-bottom: 6px;
}

.popover-list {
  max-height: 240px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.popover-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.popover-item:hover {
  background: var(--bg-secondary, #1c1c21);
}

.popover-item.item-active {
  background: rgba(255, 36, 66, 0.08);
  border: 1px solid rgba(255, 36, 66, 0.2);
}

.popover-item-info {
  flex: 1;
  min-width: 0;
}

.popover-item-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main, #f4f4f5);
  display: flex;
  align-items: center;
  gap: 6px;
}

.popover-item-sub {
  font-size: 11px;
  color: var(--text-sub, #a1a1aa);
  margin-top: 2px;
}

.popover-active-check {
  color: #ff2442;
  font-weight: 700;
  font-size: 15px;
}

.popover-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  margin-top: 6px;
  border-top: 1px solid var(--border-color, #27272a);
}

.popover-footer-btn {
  background: transparent;
  border: none;
  color: var(--text-sub, #a1a1aa);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: color 0.15s ease;
}

.popover-footer-btn:hover {
  color: #ff2442;
}

/* 发布目标提示横幅 */
.publish-target-banner {
  background: rgba(255, 36, 66, 0.04);
  border: 1px solid rgba(255, 36, 66, 0.18);
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.target-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.target-account-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main, #f4f4f5);
}

.target-account-id {
  color: var(--text-sub, #a1a1aa);
  font-size: 13px;
}

.target-switch-btn {
  background: transparent;
  border: 1px solid rgba(255, 36, 66, 0.3);
  color: #ff2442;
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.15s ease;
}

.target-switch-btn:hover {
  background: rgba(255, 36, 66, 0.1);
}

/* 管理弹窗列表 */
.manage-account-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
}

.manage-account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--bg-secondary, #1c1c21);
  border-radius: 12px;
  border: 1px solid var(--border-color, #27272a);
  gap: 14px;
}

.manage-account-item.item-active {
  border-color: rgba(255, 36, 66, 0.45);
  background: rgba(255, 36, 66, 0.04);
}

.manage-account-info {
  flex: 1;
  min-width: 0;
}

.manage-account-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main, #f4f4f5);
}

.active-badge {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.manage-account-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 标签与图片预览 */
.xhs-tag {
  padding: 6px 14px;
  background-color: rgba(255, 36, 66, 0.08);
  color: #ff2442;
  border: 1px solid rgba(255, 36, 66, 0.2);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.xhs-tag:hover {
  background-color: rgba(255, 36, 66, 0.15);
  transform: translateY(-1px);
}

.preview-image-wrapper {
  flex-shrink: 0;
  width: 120px;
  height: 160px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.preview-image-wrapper:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: #ff2442;
}

:deep(.n-image) {
  width: 100%;
  height: 100%;
  display: block;
}

:deep(.n-image img) {
  width: 100%;
  height: 100%;
  object-fit: cover !important;
}
</style>
